from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, UTC
from pydantic import EmailStr
from typing import Optional


# Defining Users table

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    todos: list["Todo"] = Relationship(back_populates="owner")


# Defining Tasks table

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    task_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory= lambda: datetime.now(UTC))
    user_id: int = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="todos")


# Defining Schemas

# User Creating request
class UserCreate(SQLModel):
    username: EmailStr
    password: str

# User response 
class UserResponse(SQLModel):
    id: int
    username: EmailStr

# Create To do task
class TodoCreate(SQLModel):
    title: str
    description: str

# Updating the task
class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_completed: Optional[bool] = None

# Task response
class TodoResponse(SQLModel):
    id: int
    title: str
    description: Optional[str]
    task_completed: bool
