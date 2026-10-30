from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from database import get_session
from models import Todo, TodoCreate, TodoResponse, TodoUpdate, User
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from security import decode_token




router = APIRouter(prefix="/todos", tags=["Todos"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Defining a function called get_current_user to get user information
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session)
) -> User:

    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)

    if not payload:
        raise invalid_token_exception

    if payload.get("type") != "access":
        raise invalid_token_exception

    email = payload.get("sub")


    if not email:
        raise invalid_token_exception

    user = session.exec(
        select(User).where(User.username == email)
    ).first()

    if not user:
        raise invalid_token_exception

    return user

# Endpoint for creating a to do task
@router.post("/", response_model=TodoResponse)
def create_todo(todo_data: TodoCreate,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
    
    
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        user_id=current_user.id
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo

# Get all tasks associated with the user
@router.get("/", response_model=list[TodoResponse])
def get_my_todos(session: Session = Depends(get_session),
                 current_user: User = Depends(get_current_user)):
    statement = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    return statement


# Get a specific to do task from id
@router.get("/{todoID}", response_model=TodoResponse)
def get_todo(
    todoID: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    todo = session.exec(select(Todo).where(
        Todo.id == todoID,
        Todo.user_id == current_user.id)
    ).first()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No to do task found.")

    return todo

# Updating a specific task
@router.put("/{todoID}", response_model=TodoResponse)
def update_todo(todoID: int,
                todo_update: TodoUpdate,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):

    todo = session.exec(select(Todo).where(Todo.id == todoID, Todo.user_id == current_user.id)).first()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No to do task found.")

    update_data = todo_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo