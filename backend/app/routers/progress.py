from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap, DailyPlan, Interview
from app.schemas import (
    ProgressOverview,
    RoadmapProgress,
    SkillRadarData,
    LearningStreak,
    WeeklySummary,
)

router = APIRouter(prefix="/api/progress", tags=["progress"])


def _calculate_roadmap_completion(roadmap: Roadmap) -> float:
    """Calculate completion percentage for a roadmap."""
    if roadmap.total_weeks == 0:
        return 0.0
    
    total_days = roadmap.total_weeks * 7  # Approximate
    completed_days = (roadmap.current_week - 1) * 7 + roadmap.current_day - 1
    
    return min(100.0, round((completed_days / total_days) * 100, 1))


def _get_weeks_progress(roadmap: Roadmap, db: Session) -> list[dict]:
    """Get progress for each week in the roadmap."""
    weeks_progress = []
    
    for week_num in range(1, roadmap.total_weeks + 1):
        # Get daily plans for this week
        daily_plans = (
            db.query(DailyPlan)
            .filter(DailyPlan.roadmap_id == roadmap.id, DailyPlan.week == week_num)
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
        
        is_current_week = week_num == roadmap.current_week
        is_completed = week_num < roadmap.current_week
        
        weeks_progress.append({
            "week": week_num,
            "is_current": is_current_week,
            "is_completed": is_completed,
            "completion_rate": completion_rate,
            "tasks_completed": completed_tasks,
            "tasks_total": total_tasks,
        })
    
    return weeks_progress


@router.get("/overview", response_model=ProgressOverview)
def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get overall progress overview for the user."""
    # Get all roadmaps
    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id)
        .all()
    )
    
    # Calculate overall completion
    total_completion = 0.0
    if roadmaps:
        for roadmap in roadmaps:
            total_completion += _calculate_roadmap_completion(roadmap)
        overall_completion = round(total_completion / len(roadmaps), 1)
    else:
        overall_completion = 0.0
    
    # Get active roadmap progress
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.is_active == True)
        .first()
    )
    
    active_roadmap_progress = {}
    if active_roadmap:
        active_roadmap_progress = {
            "roadmap_id": active_roadmap.id,
            "title": active_roadmap.content.get("title", "Untitled Roadmap") if active_roadmap.content else "Untitled Roadmap",
            "current_week": active_roadmap.current_week,
            "total_weeks": active_roadmap.total_weeks,
            "completion_percentage": _calculate_roadmap_completion(active_roadmap),
        }
    
    # Get weekly completion for the last 4 weeks
    weekly_completion = []
    for week_offset in range(3, -1, -1):
        week_start = datetime.now() - timedelta(days=week_offset * 7)
        week_end = week_start + timedelta(days=7)
        
        # Count tasks completed this week
        plans = (
            db.query(DailyPlan)
            .filter(
                DailyPlan.user_id == current_user.id,
                DailyPlan.created_at >= week_start,
                DailyPlan.created_at < week_end,
            )
            .all()
        )
        
        tasks_completed = 0
        for plan in plans:
            tasks = plan.tasks or []
            tasks_completed += sum(1 for t in tasks if t.get("completed", False))
        
        weekly_completion.append({
            "week": f"Week {week_offset + 1}",
            "tasks_completed": tasks_completed,
            "date_range": f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}",
        })
    
    # Calculate total hours spent
    all_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == current_user.id)
        .all()
    )
    
    total_hours = 0
    for plan in all_plans:
        tasks = plan.tasks or []
        for task in tasks:
            if task.get("completed", False):
                duration = task.get("duration_minutes", 30)
                total_hours += duration / 60
    
    # Identify skills improved (from completed tasks)
    skills_worked_on = set()
    for plan in all_plans:
        tasks = plan.tasks or []
        for task in tasks:
            if task.get("completed", False):
                # Try to extract skill from task title or type
                task_title = task.get("title", "").lower()
                task_type = task.get("type", "").lower()
                
                # Simple skill extraction based on keywords
                skill_keywords = {
                    "python", "java", "javascript", "react", "node", "sql",
                    "dsa", "algorithm", "data structure", "system design",
                    "machine learning", "ai", "frontend", "backend", "fullstack"
                }
                
                for keyword in skill_keywords:
                    if keyword in task_title or keyword in task_type:
                        skills_worked_on.add(keyword.title())
    
    return ProgressOverview(
        overall_completion=overall_completion,
        active_roadmap_progress=active_roadmap_progress,
        weekly_completion=weekly_completion,
        total_hours_spent=int(total_hours),
        skills_improved=list(skills_worked_on)[:10],
    )


@router.get("/roadmap/{roadmap_id}", response_model=RoadmapProgress)
def get_roadmap_progress(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed progress for a specific roadmap."""
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id, Roadmap.user_id == current_user.id)
        .first()
    )
    
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    weeks_progress = _get_weeks_progress(roadmap, db)
    
    return RoadmapProgress(
        roadmap_id=roadmap.id,
        title=roadmap.content.get("title", "Untitled Roadmap") if roadmap.content else "Untitled Roadmap",
        total_weeks=roadmap.total_weeks,
        current_week=roadmap.current_week,
        current_day=roadmap.current_day,
        completion_percentage=_calculate_roadmap_completion(roadmap),
        weeks_progress=weeks_progress,
    )


@router.get("/skills", response_model=SkillRadarData)
def get_skills_radar_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get skill radar chart data."""
    # Define skill categories for campus placements
    skill_categories = [
        "Data Structures & Algorithms",
        "Programming Languages",
        "System Design",
        "Problem Solving",
        "Communication",
        "Projects",
    ]
    
    # Get current skill levels from user profile
    user_skills = current_user.skills or {}
    
    current_levels = []
    target_levels = []
    
    for category in skill_categories:
        # Map category to skill keys in user skills
        skill_key = category.lower().replace(" & ", "_").replace(" ", "_")
        
        # Get current level
        if skill_key in user_skills:
            skill_data = user_skills[skill_key]
            if isinstance(skill_data, dict):
                level = skill_data.get("level", 3)
            elif isinstance(skill_data, (int, float)):
                level = skill_data
            else:
                level = 3
        else:
            # Default level based on progress
            level = 3
        
        current_levels.append(min(10, int(level)))
        target_levels.append(10)  # Target is always 10
    
    return SkillRadarData(
        categories=skill_categories,
        current_levels=current_levels,
        target_levels=target_levels,
    )


@router.get("/streak", response_model=LearningStreak)
def get_learning_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current learning streak information."""
    # Get all daily plans ordered by date
    all_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == current_user.id)
        .order_by(DailyPlan.created_at.desc())
        .all()
    )
    
    if not all_plans:
        return LearningStreak(
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
            streak_history=[],
        )
    
    # Calculate current streak
    current_streak = 0
    last_date = None
    streak_history = []
    
    for plan in all_plans:
        plan_date = plan.created_at.date()
        
        if last_date is None:
            # First (most recent) plan
            current_streak = 1
            last_date = plan_date
            
            # Check if last activity was today or yesterday
            today = datetime.now().date()
            days_diff = (today - plan_date).days
            
            if days_diff > 1:
                # Streak is broken
                current_streak = 0
        else:
            days_diff = (last_date - plan_date).days
            
            if days_diff <= 1:
                # Consecutive day
                current_streak += 1
                last_date = plan_date
            else:
                # Gap found, stop counting
                break
        
        # Count completed tasks for this day
        tasks = plan.tasks or []
        completed_count = sum(1 for t in tasks if t.get("completed", False))
        
        streak_history.append({
            "date": plan.created_at.isoformat(),
            "tasks_completed": completed_count,
            "week": plan.week,
            "day": plan.day,
        })
    
    # Calculate longest streak
    longest_streak = current_streak
    
    # Generate streak history for last 7 days
    last_7_days = []
    today = datetime.now().date()
    
    for i in range(7):
        date = today - timedelta(days=i)
        
        # Find plans for this date
        plans_for_date = [
            p for p in all_plans 
            if p.created_at.date() == date
        ]
        
        if plans_for_date:
            total_completed = sum(
                sum(1 for t in (p.tasks or []) if t.get("completed", False))
                for p in plans_for_date
            )
            last_7_days.append({
                "date": date.isoformat(),
                "active": True,
                "tasks_completed": total_completed,
            })
        else:
            last_7_days.append({
                "date": date.isoformat(),
                "active": False,
                "tasks_completed": 0,
            })
    
    return LearningStreak(
        current_streak=current_streak,
        longest_streak=max(longest_streak, current_streak),
        last_activity_date=all_plans[0].created_at if all_plans else None,
        streak_history=last_7_days,
    )


@router.get("/weekly-summary", response_model=WeeklySummary)
def get_weekly_summary(
    week_offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get weekly progress summary."""
    # Calculate week range
    end_date = datetime.now() - timedelta(days=week_offset * 7)
    start_date = end_date - timedelta(days=7)
    
    # Get daily plans for this week
    plans = (
        db.query(DailyPlan)
        .filter(
            DailyPlan.user_id == current_user.id,
            DailyPlan.created_at >= start_date,
            DailyPlan.created_at < end_date,
        )
        .all()
    )
    
    # Calculate task stats
    tasks_completed = 0
    tasks_total = 0
    skills_worked = set()
    
    for plan in plans:
        tasks = plan.tasks or []
        for task in tasks:
            tasks_total += 1
            if task.get("completed", False):
                tasks_completed += 1
                # Extract skills from task
                title = task.get("title", "").lower()
                for skill in ["python", "java", "dsa", "sql", "react", "system design"]:
                    if skill in title:
                        skills_worked.add(skill.title())
    
    completion_rate = 0.0
    if tasks_total > 0:
        completion_rate = round((tasks_completed / tasks_total) * 100, 1)
    
    # Get interviews taken this week
    interviews = (
        db.query(Interview)
        .filter(
            Interview.user_id == current_user.id,
            Interview.created_at >= start_date,
            Interview.created_at < end_date,
        )
        .all()
    )
    
    interviews_taken = len(interviews)
    
    # Calculate average interview score
    scores = [i.score for i in interviews if i.score is not None]
    average_score = round(sum(scores) / len(scores), 1) if scores else None
    
    # Determine week number
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.is_active == True)
        .first()
    )
    week_number = active_roadmap.current_week if active_roadmap else 1
    
    return WeeklySummary(
        week_number=week_number,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        tasks_completed=tasks_completed,
        tasks_total=tasks_total,
        completion_rate=completion_rate,
        skills_worked_on=list(skills_worked),
        interviews_taken=interviews_taken,
        average_interview_score=average_score,
    )
