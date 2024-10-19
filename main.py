import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.courses import routes as course_routes
from backend.api.users import routes as user_routes
from backend.api.auth import routes as auth_routes
from backend.api.lessons import routes as lesson_routes
from backend.api.notifications import routes as notification_routes
from backend.api.analytics import routes as analytics_routes
from backend.core.config.settings import settings

# Ensure Brave Search API key is set
os.environ["BRAVE_SEARCH_API_KEY"] = settings.BRAVE_SEARCH_API_KEY

app = FastAPI(title="AI-Powered Learning Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(course_routes.router, prefix="/api/courses", tags=["Courses"])
app.include_router(lesson_routes.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(notification_routes.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Analytics"])

@app.on_event("startup")
async def startup_event():
    # Initialize any services or connections here
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up any resources here
    pass

@app.get("/")
async def root():
    return {"message": "Welcome to the Education Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
