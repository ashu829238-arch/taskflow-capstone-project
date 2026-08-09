from backend.database import SessionLocal
from backend.models import Project, Task, User


def seed():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "seed@example.com").first()
        if not user:
            user = User(name="Seed User", email="seed@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)

        project = db.query(Project).filter(Project.name == "Operations Engineering").first()
        if not project:
            project = Project(name="Operations Engineering", owner_id=user.id)
            db.add(project)
            db.commit()
            db.refresh(project)

        if db.query(Task).count() == 0:
            for i in range(1, 11):
                db.add(
                    Task(
                        title=f"Seed Task {i}",
                        priority=["low", "medium", "high"][i % 3],
                        status=["todo", "in_progress", "done"][i % 3],
                        due_date=None,
                        project_id=project.id,
                    )
                )
            db.commit()

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
