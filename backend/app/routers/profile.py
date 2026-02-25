from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap, DailyPlan, Interview
from app.schemas import (
    UserProfile,
    UserProfileUpdate,
    SkillsUpdateRequest,
    UserProgressStats,
    DashboardStats,
)

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=UserProfile)
def update_profile(
    body: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/progress", response_model=UserProgressStats)
def get_learning_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's learning progress statistics."""
    # Count roadmaps
    total_roadmaps = (
        db.query(Roadmap).filter(Roadmap.user_id == current_user.id).count()
    )
    active_roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.is_active == True)
        .count()
    )
    completed_roadmaps = (
        db.query(Roadmap)
        .filter(
            Roadmap.user_id == current_user.id,
            Roadmap.current_week >= Roadmap.total_weeks,
        )
        .count()
    )

    # Count interviews
    total_interviews = (
        db.query(Interview).filter(Interview.user_id == current_user.id).count()
    )
    
    # Calculate average interview score
    interview_scores = (
        db.query(Interview.score)
        .filter(Interview.user_id == current_user.id, Interview.score.isnot(None))
        .all()
    )
    average_score = None
    if interview_scores:
        scores = [s[0] for s in interview_scores]
        average_score = round(sum(scores) / len(scores), 1)

    # Count tasks
    daily_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == current_user.id)
        .all()
    )
    
    total_tasks = 0
    completed_tasks = 0
    for plan in daily_plans:
        tasks = plan.tasks or []
        total_tasks += len(tasks)
        completed_tasks += sum(1 for t in tasks if t.get("completed", False))

    completion_rate = 0.0
    if total_tasks > 0:
        completion_rate = round((completed_tasks / total_tasks) * 100, 1)

    return UserProgressStats(
        total_roadmaps=total_roadmaps,
        active_roadmaps=active_roadmaps,
        completed_roadmaps=completed_roadmaps,
        total_interviews=total_interviews,
        average_interview_score=average_score,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=completion_rate,
    )


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics for the user."""
    # Get weekly progress (last 4 weeks)
    weekly_progress = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "tasks_completed": [0, 0, 0, 0],
        "hours_spent": [0, 0, 0, 0],
    }

    # Calculate tasks completed per week from daily plans
    daily_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == current_user.id)
        .order_by(DailyPlan.week.desc())
        .limit(28)  # Last 4 weeks
        .all()
    )

    week_task_counts = {}
    for plan in daily_plans:
        week_key = f"Week {plan.week}"
        if week_key not in week_task_counts:
            week_task_counts[week_key] = {"completed": 0, "hours": 0}
        
        tasks = plan.tasks or []
        for task in tasks:
            if task.get("completed", False):
                week_task_counts[week_key]["completed"] += 1
                # Estimate hours from task duration
                duration = task.get("duration_minutes", 30)
                week_task_counts[week_key]["hours"] += duration / 60

    # Update weekly progress with actual data
    for i, label in enumerate(weekly_progress["labels"]):
        if label in week_task_counts:
            weekly_progress["tasks_completed"][i] = week_task_counts[label]["completed"]
            weekly_progress["hours_spent"][i] = round(week_task_counts[label]["hours"], 1)

    # Get skill levels from user skills
    skill_levels = {}
    if current_user.skills and isinstance(current_user.skills, dict):
        for skill_name, skill_data in current_user.skills.items():
            if isinstance(skill_data, dict):
                skill_levels[skill_name] = skill_data.get("level", 0)
            else:
                skill_levels[skill_name] = skill_data

    # Calculate streak (simplified - based on daily plan activity)
    streak_days = 0
    last_plan = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == current_user.id)
        .order_by(DailyPlan.created_at.desc())
        .first()
    )
    if last_plan:
        # Check if last activity was recent
        from datetime import datetime, timedelta
        days_since = (datetime.now() - last_plan.created_at).days
        if days_since <= 1:
            # Count consecutive days with activity
            all_plans = (
                db.query(DailyPlan)
                .filter(DailyPlan.user_id == current_user.id)
                .order_by(DailyPlan.created_at.desc())
                .all()
            )
            current_streak = 0
            last_date = None
            for plan in all_plans:
                plan_date = plan.created_at.date()
                if last_date is None or (last_date - plan_date).days <= 1:
                    current_streak += 1
                    last_date = plan_date
                else:
                    break
            streak_days = current_streak

    # Generate upcoming milestones
    upcoming_milestones = []
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.is_active == True)
        .first()
    )
    if active_roadmap:
        current_week = active_roadmap.current_week
        total_weeks = active_roadmap.total_weeks
        
        if current_week < total_weeks:
            upcoming_milestones.append({
                "title": f"Complete Week {current_week}",
                "type": "weekly_goal",
                "due_in_days": 7,
            })
        if current_week + 1 <= total_weeks:
            upcoming_milestones.append({
                "title": f"Start Week {current_week + 1}",
                "type": "milestone",
                "due_in_days": 7,
            })

    return DashboardStats(
        weekly_progress=weekly_progress,
        skill_levels=skill_levels,
        streak_days=streak_days,
        upcoming_milestones=upcoming_milestones,
    )


@router.post("/skills", response_model=UserProfile)
def update_skills(
    body: SkillsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user's skills assessment."""
    current_user.skills = body.skills
    db.commit()
    db.refresh(current_user)
    return current_user
