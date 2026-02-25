from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap
from app.schemas import RoadmapResponse, RoadmapListResponse
from app.services.bedrock import bedrock_service
from app.services.prompts import ROADMAP_SYSTEM_PROMPT, get_roadmap_prompt

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


@router.post("/generate", response_model=RoadmapResponse)
def generate_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_profile = {
        "college": current_user.college,
        "college_tier": current_user.college_tier,
        "degree": current_user.degree,
        "major": current_user.major,
        "is_cs_background": current_user.is_cs_background,
        "target_role": current_user.target_role,
        "target_companies": current_user.target_companies,
        "hours_per_day": current_user.hours_per_day,
        "days_per_week": current_user.days_per_week,
        "skills": current_user.skills,
        "current_year": current_user.current_year,
    }

    raw_response = bedrock_service.invoke_model(
        ROADMAP_SYSTEM_PROMPT,
        get_roadmap_prompt(user_profile),
    )
    parsed_json = bedrock_service.parse_json_response(raw_response)

    # Deactivate existing active roadmaps
    db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.is_active == True,
    ).update({"is_active": False})

    roadmap = Roadmap(
        user_id=current_user.id,
        content=parsed_json,
        total_weeks=parsed_json.get("total_weeks", 8),
        is_active=True,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap


@router.get("", response_model=RoadmapResponse)
def get_active_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.is_active == True)
        .first()
    )
    if roadmap is None:
        raise HTTPException(status_code=404, detail="No active roadmap found")
    return roadmap


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap_by_id(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id, Roadmap.user_id == current_user.id)
        .first()
    )
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


@router.put("/{roadmap_id}/activate", response_model=RoadmapResponse)
def activate_roadmap(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Switch active roadmap. Deactivates current active roadmap and activates the specified one."""
    # Check if the roadmap exists and belongs to the user
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id, Roadmap.user_id == current_user.id)
        .first()
    )
    
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    if roadmap.is_active:
        return roadmap  # Already active
    
    # Deactivate all user's roadmaps
    db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.is_active == True,
    ).update({"is_active": False})
    
    # Activate the specified roadmap
    roadmap.is_active = True
    db.commit()
    db.refresh(roadmap)
    
    return roadmap


@router.delete("/{roadmap_id}", status_code=204)
def delete_roadmap(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a roadmap. If it was the active roadmap, another roadmap may become active."""
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id, Roadmap.user_id == current_user.id)
        .first()
    )
    
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    was_active = roadmap.is_active
    
    db.delete(roadmap)
    db.commit()
    
    # If we deleted the active roadmap, try to activate another one
    if was_active:
        another_roadmap = (
            db.query(Roadmap)
            .filter(Roadmap.user_id == current_user.id)
            .order_by(Roadmap.created_at.desc())
            .first()
        )
        if another_roadmap:
            another_roadmap.is_active = True
            db.commit()
    
    return None


@router.get("/list/all", response_model=RoadmapListResponse)
def list_all_roadmaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all roadmaps for the current user."""
    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id)
        .order_by(Roadmap.is_active.desc(), Roadmap.created_at.desc())
        .all()
    )
    
    return RoadmapListResponse(
        roadmaps=roadmaps,
        total=len(roadmaps),
    )
