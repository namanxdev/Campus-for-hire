from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── User ──────────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    auth_provider: Optional[str] = None
    college: Optional[str] = None
    college_tier: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    current_year: Optional[int] = None
    is_cs_background: bool = False
    target_role: Optional[str] = None
    target_companies: Optional[list[str]] = None
    hours_per_day: int = 2
    days_per_week: int = 5
    preferred_language: str = "en"
    skills: Optional[dict] = None
    onboarding_completed: bool = False


class UserProfileUpdate(BaseModel):
    college: Optional[str] = None
    college_tier: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    current_year: Optional[int] = None
    is_cs_background: Optional[bool] = None
    target_role: Optional[str] = None
    target_companies: Optional[list[str]] = None
    hours_per_day: Optional[int] = None
    days_per_week: Optional[int] = None
    preferred_language: Optional[str] = None
    skills: Optional[dict] = None
    onboarding_completed: Optional[bool] = None


class SkillsUpdateRequest(BaseModel):
    skills: dict


class UserProgressStats(BaseModel):
    total_roadmaps: int
    active_roadmaps: int
    completed_roadmaps: int
    total_interviews: int
    average_interview_score: Optional[float]
    total_tasks: int
    completed_tasks: int
    completion_rate: float


class DashboardStats(BaseModel):
    weekly_progress: dict
    skill_levels: dict
    streak_days: int
    upcoming_milestones: list[dict]


# ── Roadmap ───────────────────────────────────────────────────────────────

class RoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    content: dict
    pace: str
    total_weeks: int
    current_week: int
    current_day: int
    is_active: bool
    created_at: datetime


class RoadmapListResponse(BaseModel):
    roadmaps: list[RoadmapResponse]
    total: int


# ── Daily Plan ────────────────────────────────────────────────────────────

class DailyPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    roadmap_id: str
    user_id: str
    week: int
    day: int
    tasks: list[dict]
    created_at: datetime


class TaskCompleteRequest(BaseModel):
    task_id: str
    completed: bool


# ── Interview ─────────────────────────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    role: str
    company: Optional[str] = None


class InterviewRespondRequest(BaseModel):
    interview_id: str
    message: str


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    role: str
    company: Optional[str] = None
    messages: list[dict]
    score: Optional[int] = None
    feedback: Optional[str] = None
    created_at: datetime


# ── JD Analysis ───────────────────────────────────────────────────────────

class JDAnalyzeRequest(BaseModel):
    job_description: str


class JDAnalyzeResponse(BaseModel):
    role: str
    company: Optional[str] = None
    required_skills: list[dict]
    user_skills: list[dict]
    gap_analysis: list[dict]
    recommendations: list[str]


# ── Translation ───────────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str
    target_language: str


class TranslateResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str


# ── Progress ──────────────────────────────────────────────────────────────

class ProgressOverview(BaseModel):
    overall_completion: float
    active_roadmap_progress: dict
    weekly_completion: list[dict]
    total_hours_spent: int
    skills_improved: list[str]


class RoadmapProgress(BaseModel):
    roadmap_id: str
    title: str
    total_weeks: int
    current_week: int
    current_day: int
    completion_percentage: float
    weeks_progress: list[dict]


class SkillRadarData(BaseModel):
    categories: list[str]
    current_levels: list[int]
    target_levels: list[int]


class LearningStreak(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    streak_history: list[dict]


class WeeklySummary(BaseModel):
    week_number: int
    start_date: str
    end_date: str
    tasks_completed: int
    tasks_total: int
    completion_rate: float
    skills_worked_on: list[str]
    interviews_taken: int
    average_interview_score: Optional[float]


# ── Content ───────────────────────────────────────────────────────────────

class ExplainRequest(BaseModel):
    concept: str
    context: Optional[str] = None
    difficulty_level: Optional[str] = "beginner"


class ExplainResponse(BaseModel):
    explanation: str
    examples: list[str]
    key_points: list[str]
    related_topics: list[str]


class ResourcesRequest(BaseModel):
    topic: str
    skill_level: Optional[str] = "intermediate"
    resource_type: Optional[str] = None


class ResourceItem(BaseModel):
    title: str
    type: str
    url: Optional[str] = None
    description: str
    difficulty: str
    estimated_time: Optional[str] = None


class ResourcesResponse(BaseModel):
    topic: str
    resources: list[ResourceItem]


class TranslateRoadmapRequest(BaseModel):
    roadmap_id: str
    target_language: str


class TranslateRoadmapResponse(BaseModel):
    roadmap_id: str
    translated_content: dict
    target_language: str


# ── Dashboard ─────────────────────────────────────────────────────────────

class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime
    metadata: Optional[dict] = None


class RecommendationItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    priority: str
    action_url: Optional[str] = None


class DashboardData(BaseModel):
    user: UserProfile
    active_roadmap: Optional[RoadmapResponse]
    progress: ProgressOverview
    today_plan: Optional[DailyPlanResponse]
    streak: LearningStreak
    recent_activities: list[ActivityItem]
    recommendations: list[RecommendationItem]
    stats: DashboardStats


class ActivitiesResponse(BaseModel):
    activities: list[ActivityItem]
    total: int
    has_more: bool


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationItem]
