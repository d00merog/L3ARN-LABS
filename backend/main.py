import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.courses import routes as courses_routes
from api.auth import routes as auth_routes
from api.lessons import routes as lessons_routes
from api.users import routes as users_routes
from core.database.db import engine, Base
from core.config.settings import settings

# Ensure Brave Search API key is set
os.environ["BRAVE_SEARCH_API_KEY"] = settings.BRAVE_SEARCH_API_KEY

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses_routes.router, prefix="/api/courses", tags=["courses"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(lessons_routes.router, prefix="/api/lessons", tags=["lessons"])
app.include_router(users_routes.router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Education Platform API"}