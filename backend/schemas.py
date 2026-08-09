from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class UserResponse(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    owner_id: int = Field(gt=0)

    @field_validator("name")
    @classmethod
    def project_name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("project name must not be blank")
        return value


class ProjectResponse(ProjectCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="todo", pattern="^(todo|in_progress|done)$")
    due_date: Optional[str] = None
    project_id: int = Field(gt=0)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(default=None, pattern="^(todo|in_progress|done)$")
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: str
    status: str
    due_date: Optional[str]
    project_id: int
    model_config = ConfigDict(from_attributes=True)


class QuickAddRequest(BaseModel):
    description: str = Field(min_length=1)
    project_id: int = Field(gt=0)

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("description must not be blank")
        return value


class TaskStats(BaseModel):
    project_id: int
    project_name: str
    task_count: int
    todo_count: int
    in_progress_count: int
    done_count: int
