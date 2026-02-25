from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap, DailyPlan, Interview
from app.schemas import (
    DashboardData,
    ActivitiesResponse,
    RecommendationsResponse,
    ActivityItem,
    RecommendationItem,
    UserProfile,
    RoadmapResponse,
    DailyPlanResponse,
    ProgressOverview,
    LearningStreak,
    DashboardStats,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _get_recent_activities(user: User, db: Session, limit: int = 10) -> list[ActivityItem]:
    """Get recent user activities from various sources."""
    activities = []
    
    # Get activities from daily plans
    daily_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id)
        .order_by(DailyPlan.created_at.desc())
        .limit(limit)
        .all()
    )
    
    for plan in daily_plans:
        tasks_completed = sum(1 for t in (plan.tasks or []) if t.get("completed", False))
        if tasks_completed > 0:
            activities.append(ActivityItem(
                id=f"task_{plan.id}",
                type="task_completion",
                title="Completed Daily Tasks",
                description=f"Completed {tasks_completed} tasks in Week {plan.week}, Day {plan.day}",
                timestamp=plan.created_at,
                metadata={
                    "week": plan.week,
                    "day": plan.day,
                    "tasks_completed": tasks_completed,
                },
            ))
    
    # Get activities from interviews
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == user.id)
        .order_by(Interview.created_at.desc())
        .limit(limit)
        .all()
    )
    
    for interview in interviews:
        if interview.score is not None:
            activities.append(ActivityItem(
                id=f"interview_{interview.id}",
                type="interview_completed",
                title=f"Completed Mock Interview: {interview.role}",
                description=f"Scored {interview.score}/10 in {interview.company or 'General'} interview",
                timestamp=interview.created_at,
                metadata={
                    "role": interview.role,
                    "company": interview.company,
                    "score": interview.score,
                },
            ))
        else:
            activities.append(ActivityItem(
                id=f"interview_{interview.id}",
                type="interview_started",
                title=f"Started Mock Interview: {interview.role}",
                description=f"Started practice interview for {interview.role} role",
                timestamp=interview.created_at,
                metadata={
                    "role": interview.role,
                    "company": interview.company,
                },
            ))
    
    # Get activities from roadmap creation
    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user.id)
        .order_by(Roadmap.created_at.desc())
        .limit(limit)
        .all()
    )
    
    for roadmap in roadmaps:
        title = roadmap.content.get("title", "New Roadmap") if roadmap.content else "New Roadmap"
        activities.append(ActivityItem(
            id=f"roadmap_{roadmap.id}",
            type="roadmap_created",
            title="Created Learning Roadmap",
            description=title,
            timestamp=roadmap.created_at,
            metadata={
                "roadmap_id": roadmap.id,
                "is_active": roadmap.is_active,
            },
        ))
    
    # Sort by timestamp descending and return top items
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    return activities[:limit]


def _get_recommendations(user: User, db: Session) -> list[RecommendationItem]:
    """Generate personalized recommendations for the user."""
    recommendations = []
    
    # Check if user has an active roadmap
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user.id, Roadmap.is_active == True)
        .first()
    )
    
    if not active_roadmap:
        recommendations.append(RecommendationItem(
            id="rec_create_roadmap",
            type="roadmap",
            title="Create Your Learning Roadmap",
            description="You don't have an active learning plan. Generate a personalized roadmap based on your goals.",
            priority="high",
            action_url="/roadmap/generate",
        ))
    else:
        # Check daily plan progress
        today_plan = (
            db.query(DailyPlan)
            .filter(
                DailyPlan.roadmap_id == active_roadmap.id,
                DailyPlan.week == active_roadmap.current_week,
                DailyPlan.day == active_roadmap.current_day,
            )
            .first()
        )
        
        if today_plan:
            pending_tasks = sum(1 for t in (today_plan.tasks or []) if not t.get("completed", False))
            if pending_tasks > 0:
                recommendations.append(RecommendationItem(
                    id="rec_complete_tasks",
                    type="daily_plan",
                    title=f"Complete Today's Tasks",
                    description=f"You have {pending_tasks} pending tasks for today. Keep your streak going!",
                    priority="high",
                    action_url="/daily-plan",
                ))
        
        # Check if roadmap is progressing
        if active_roadmap.current_week == 1 and active_roadmap.current_day <= 2:
            recommendations.append(RecommendationItem(
                id="rec_get_started",
                type="getting_started",
                title="Getting Started with Your Roadmap",
                description="You're just beginning your learning journey. Start with the basics and build consistency.",
                priority="medium",
                action_url="/roadmap",
            ))
    
    # Check if user has taken any interviews
    interview_count = (
        db.query(Interview)
        .filter(Interview.user_id == user.id)
        .count()
    )
    
    if interview_count == 0:
        recommendations.append(RecommendationItem(
            id="rec_first_interview",
            type="interview",
            title="Try Your First Mock Interview",
            description="Practice makes perfect. Take a mock interview to assess your readiness.",
            priority="high",
            action_url="/interview",
        ))
    elif interview_count < 3:
        recommendations.append(RecommendationItem(
            id="rec_more_interviews",
            type="interview",
            title="Take More Mock Interviews",
            description="You've started practicing! Keep going with more interviews to improve.",
            priority="medium",
            action_url="/interview",
        ))
    
    # Check skills
    if not user.skills or (isinstance(user.skills, dict) and len(user.skills) < 3):
        recommendations.append(RecommendationItem(
            id="rec_assess_skills",
            type="skills",
            title="Complete Skills Assessment",
            description="Update your skills profile to get better personalized recommendations.",
            priority="medium",
            action_url="/profile/skills",
        ))
    
    # Target role specific recommendations
    if user.target_role:
        recommendations.append(RecommendationItem(
            id="rec_role_resources",
            type="resources",
            title=f"Resources for {user.target_role}",
            description=f"Explore curated learning materials specifically for {user.target_role} roles.",
            priority="low",
            action_url=f"/content/resources?topic={user.target_role.replace(' ', '+')}",
        ))
    
    # General recommendations
    recommendations.append(RecommendationItem(
        id="rec_consistency",
        type="tip",
        title="Consistency is Key",
        description="Try to study at the same time every day to build a habit. Even 30 minutes daily is better than 3 hours once a week.",
        priority="low",
    ))
    
    return recommendations


def _calculate_streak(user: User, db: Session) -> LearningStreak:
    """Calculate user's learning streak."""
    all_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id)
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
    
    for plan in all_plans:
        plan_date = plan.created_at.date()
        
        if last_date is None:
            # Check if last activity was recent (within last 2 days)
            today = datetime.now().date()
            days_diff = (today - plan_date).days
            
            if days_diff <= 1:
                current_streak = 1
                last_date = plan_date
            else:
                break
        else:
            days_diff = (last_date - plan_date).days
            
            if days_diff == 1:
                current_streak += 1
                last_date = plan_date
            elif days_diff == 0:
                # Same day, continue
                continue
            else:
                break
    
    # Generate streak history
    last_7_days = []
    today = datetime.now().date()
    
    for i in range(7):
        date = today - timedelta(days=i)
        plans_for_date = [p for p in all_plans if p.created_at.date() == date]
        
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
        longest_streak=max(current_streak, 0),
        last_activity_date=all_plans[0].created_at,
        streak_history=last_7_days,
    )


def _calculate_progress_overview(user: User, db: Session) -> ProgressOverview:
    """Calculate progress overview for the user."""
    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user.id)
        .all()
    )
    
    # Calculate overall completion
    if roadmaps:
        total_completion = sum(
            min(100, ((r.current_week - 1) * 7 + r.current_day - 1) / max(1, r.total_weeks * 7) * 100)
            for r in roadmaps
        )
        overall_completion = round(total_completion / len(roadmaps), 1)
    else:
        overall_completion = 0.0
    
    # Get active roadmap progress
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user.id, Roadmap.is_active == True)
        .first()
    )
    
    active_roadmap_progress = {}
    if active_roadmap:
        title = "Untitled Roadmap"
        if active_roadmap.content and isinstance(active_roadmap.content, dict):
            title = active_roadmap.content.get("title", "Untitled Roadmap")
        
        active_roadmap_progress = {
            "roadmap_id": active_roadmap.id,
            "title": title,
            "current_week": active_roadmap.current_week,
            "total_weeks": active_roadmap.total_weeks,
            "completion_percentage": round(
                ((active_roadmap.current_week - 1) * 7 + active_roadmap.current_day - 1) / 
                max(1, active_roadmap.total_weeks * 7) * 100, 1
            ),
        }
    
    # Weekly completion
    weekly_completion = []
    for week_offset in range(3, -1, -1):
        week_end = datetime.now() - timedelta(days=week_offset * 7)
        week_start = week_end - timedelta(days=7)
        
        plans = (
            db.query(DailyPlan)
            .filter(
                DailyPlan.user_id == user.id,
                DailyPlan.created_at >= week_start,
                DailyPlan.created_at < week_end,
            )
            .all()
        )
        
        tasks_completed = sum(
            sum(1 for t in (p.tasks or []) if t.get("completed", False))
            for p in plans
        )
        
        weekly_completion.append({
            "week": f"Week {4 - week_offset}",
            "tasks_completed": tasks_completed,
            "date_range": f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}",
        })
    
    # Total hours spent
    all_plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id)
        .all()
    )
    
    total_hours = sum(
        sum((t.get("duration_minutes", 30) or 30) / 60 for t in (p.tasks or []) if t.get("completed", False))
        for p in all_plans
    )
    
    return ProgressOverview(
        overall_completion=overall_completion,
        active_roadmap_progress=active_roadmap_progress,
        weekly_completion=weekly_completion,
        total_hours_spent=int(total_hours),
        skills_improved=[],
    )


def _get_dashboard_stats(user: User, db: Session) -> DashboardStats:
    """Get dashboard statistics."""
    # Weekly progress
    weekly_progress = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "tasks_completed": [0, 0, 0, 0],
        "hours_spent": [0, 0, 0, 0],
    }
    
    # Skill levels
    skill_levels = {}
    if user.skills and isinstance(user.skills, dict):
        for skill_name, skill_data in user.skills.items():
            if isinstance(skill_data, dict):
                skill_levels[skill_name] = skill_data.get("level", 0)
            else:
                skill_levels[skill_name] = skill_data
    
    # Upcoming milestones
    upcoming_milestones = []
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user.id, Roadmap.is_active == True)
        .first()
    )
    
    if active_roadmap:
        if active_roadmap.current_week < active_roadmap.total_weeks:
            upcoming_milestones.append({
                "title": f"Complete Week {active_roadmap.current_week}",
                "type": "weekly_goal",
                "due_in_days": 7,
            })
    
    return DashboardStats(
        weekly_progress=weekly_progress,
        skill_levels=skill_levels,
        streak_days=0,
        upcoming_milestones=upcoming_milestones,
    )


@router.get("", response_model=DashboardData)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all dashboard data in a single call."""
    # Get user profile
    user_profile = UserProfile.model_validate(current_user)
    
    # Get active roadmap
    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.is_active == True)
        .first()
    )
    
    roadmap_response = None
    if active_roadmap:
        roadmap_response = RoadmapResponse.model_validate(active_roadmap)
    
    # Get today's plan
    today_plan = None
    if active_roadmap:
        today_plan = (
            db.query(DailyPlan)
            .filter(
                DailyPlan.roadmap_id == active_roadmap.id,
                DailyPlan.week == active_roadmap.current_week,
                DailyPlan.day == active_roadmap.current_day,
            )
            .first()
        )
    
    today_plan_response = None
    if today_plan:
        today_plan_response = DailyPlanResponse.model_validate(today_plan)
    
    # Get all components
    progress = _calculate_progress_overview(current_user, db)
    streak = _calculate_streak(current_user, db)
    activities = _get_recent_activities(current_user, db, limit=10)
    recommendations = _get_recommendations(current_user, db)
    stats = _get_dashboard_stats(current_user, db)
    
    return DashboardData(
        user=user_profile,
        active_roadmap=roadmap_response,
        progress=progress,
        today_plan=today_plan_response,
        streak=streak,
        recent_activities=activities,
        recommendations=recommendations,
        stats=stats,
    )


@router.get("/activities", response_model=ActivitiesResponse)
def get_activities(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent activities with pagination."""
    all_activities = _get_recent_activities(current_user, db, limit=limit + offset)
    activities = all_activities[offset:offset + limit]
    
    return ActivitiesResponse(
        activities=activities,
        total=len(all_activities),
        has_more=len(all_activities) > offset + limit,
    )


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get personalized recommendations."""
    recommendations = _get_recommendations(current_user, db)
    
    return RecommendationsResponse(
        recommendations=recommendations,
    )
