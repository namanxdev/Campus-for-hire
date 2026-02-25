import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    auth_provider = Column(String)
    college = Column(String, nullable=True)
    college_tier = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    major = Column(String, nullable=True)
    current_year = Column(Integer, nullable=True)
    is_cs_background = Column(Boolean, default=False)
    target_role = Column(String, nullable=True)
    target_companies = Column(JSON, nullable=True)
    hours_per_day = Column(Integer, default=2)
    days_per_week = Column(Integer, default=5)
    preferred_language = Column(String, default="en")
    skills = Column(JSON, nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    content = Column(JSON)
    pace = Column(String, default="standard")
    total_weeks = Column(Integer)
    current_week = Column(Integer, default=1)
    current_day = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id = Column(String, ForeignKey("roadmaps.id"))
    user_id = Column(String, ForeignKey("users.id"))
    week = Column(Integer)
    day = Column(Integer)
    tasks = Column(JSON)
    created_at = Column(DateTime, default=func.now())


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    role = Column(String)
    company = Column(String, nullable=True)
    messages = Column(JSON)
    score = Column(Integer, nullable=True)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
