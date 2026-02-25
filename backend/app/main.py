from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import engine, Base
from app.middleware import ErrorHandlerMiddleware, RateLimitMiddleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
)
from app.routers import (
    profile,
    roadmap,
    daily_plan,
    interview,
    jd,
    translate,
    progress,
    content,
    dashboard,
)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Campus-to-Hire API",
    description="AI-powered personalization platform for Indian campus placements",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (100 requests/minute default, 10 for auth endpoints)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    burst_size=20,
)

# Global error handling middleware (must be last to catch all errors)
app.add_middleware(ErrorHandlerMiddleware)

# Register exception handlers
app.add_exception_handler(Exception, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Register routers
app.include_router(profile.router)
app.include_router(roadmap.router)
app.include_router(daily_plan.router)
app.include_router(interview.router)
app.include_router(jd.router)
app.include_router(translate.router)
app.include_router(progress.router)
app.include_router(content.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Campus-to-Hire API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
