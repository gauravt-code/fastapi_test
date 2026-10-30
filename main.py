from fastapi import FastAPI, HTTPException
from database import create_db_table
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
import jwt
from models import User, UserCreate
from security import generate_hashed_password, verify_password, create_access_token, create_refresh_token, decode_token
from routers import auth
from routers import todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting initialization..")
    create_db_table()
    yield


app = FastAPI(
    title = "To-do application",
    description="A to-do app to keep track of tasks",
    lifespan=lifespan
)

# Initial page
@app.get("/")
def root():
    return {"message": "This is a to-do application"}

app.include_router(auth.router)
app.include_router(todos.router)