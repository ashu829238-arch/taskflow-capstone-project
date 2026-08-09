import time
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from .algorithms import binary_search, insertion_sort, linear_search
from .database import engine, get_db
from .models import Base, Project, Task, User
from .quick_add import build_prompt, parse_quick_add
from .schemas import (
    ProjectCreate,
    ProjectResponse,
    QuickAddRequest,
    TaskCreate,
    TaskResponse,
    TaskStats,
    TaskUpdate,
    UserCreate,
    UserResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

FRONTEND_ORIGIN = "http://127.0.0.1:5500"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(
        f"{request.method} {request.url.path} "
        f"{elapsed_ms:.2f} ms"
    )
    return response


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(name=payload.name, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project).order_by(Project.id)).all()


@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    owner = db.get(User, payload.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    project = Project(name=payload.name, owner_id=payload.owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def task_to_dict(task: Task):
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "project_id": task.project_id,
        "priority_rank": {"low": 1, "medium": 2, "high": 3}[task.priority],
    }


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    sort: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    tasks = db.scalars(select(Task)).all()
    records = [task_to_dict(task) for task in tasks]

    if sort == "priority":
        insertion_sort(records, "priority_rank")
    elif sort == "due_date":
        # Keep None values comparable by using a simple string sentinel.
        for record in records:
            record["due_sort"] = record["due_date"] or ""
        insertion_sort(records, "due_sort")

    for record in records:
        record.pop("priority_rank", None)
        record.pop("due_sort", None)

    return records


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    project = db.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks/search", response_model=TaskResponse)
def search_tasks(
    title: str,
    algo: str = Query(default="binary", pattern="^(binary|linear)$"),
    db: Session = Depends(get_db),
):
    tasks = db.scalars(select(Task)).all()
    index = [{"id": task.id, "title": task.title} for task in tasks]

    if algo == "binary":
        insertion_sort(index, "title")
        position = binary_search(index, title, "title")
    else:
        position = linear_search(index, title, "title")

    if position == -1:
        raise HTTPException(status_code=404, detail="Task title not found")

    return db.get(Task, index[position]["id"])


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted", "id": task_id}


@app.get("/projects/stats", response_model=list[TaskStats])
def project_task_stats(db: Session = Depends(get_db)):
    todo_case = case((Task.status == "todo", 1), else_=0)
    progress_case = case((Task.status == "in_progress", 1), else_=0)
    done_case = case((Task.status == "done", 1), else_=0)

    statement = (
        select(
            Project.id.label("project_id"),
            Project.name.label("project_name"),
            func.count(Task.id).label("task_count"),
            func.sum(todo_case).label("todo_count"),
            func.sum(progress_case).label("in_progress_count"),
            func.sum(done_case).label("done_count"),
        )
        .outerjoin(Task, Task.project_id == Project.id)
        .group_by(Project.id, Project.name)
        .order_by(Project.id)
    )

    rows = db.execute(statement).all()

    return [
        {
            "project_id": row.project_id,
            "project_name": row.project_name,
            "task_count": row.task_count,
            "todo_count": row.todo_count or 0,
            "in_progress_count": row.in_progress_count or 0,
            "done_count": row.done_count or 0,
        }
        for row in rows
    ]


@app.post("/tasks/quick-add", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def quick_add(payload: QuickAddRequest, db: Session = Depends(get_db)):
    project = db.get(Project, payload.project_id)
    if not project:
        # The capstone explicitly requires 422 for an invalid quick-add project_id.
        raise HTTPException(status_code=422, detail="project_id does not reference an existing project")

    prompt = build_prompt(payload.description)
    parsed = parse_quick_add(prompt[1]["content"])

    candidate = {
        "title": parsed["title"],
        "priority": parsed["priority"],
        "status": "todo",
        "due_date": parsed["due_date_hint"],
        "project_id": payload.project_id,
    }

    validated = TaskCreate(**candidate)
    task = Task(**validated.model_dump())

    db.add(task)
    db.commit()
    db.refresh(task)
    return task
