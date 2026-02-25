from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.schemas import JDAnalyzeRequest, JDAnalyzeResponse
from app.services.bedrock import bedrock_service
from app.services.prompts import JD_SYSTEM_PROMPT, get_jd_analysis_prompt

router = APIRouter(prefix="/api/jd", tags=["jd"])


@router.post("/analyze", response_model=JDAnalyzeResponse)
def analyze_jd(
    body: JDAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JDAnalyzeResponse:
    """Analyze a job description and return a skill gap report against the user's current skills."""
    user_skills = current_user.skills or {}

    raw = bedrock_service.invoke_model(
        JD_SYSTEM_PROMPT,
        get_jd_analysis_prompt(body.job_description, user_skills),
    )

    try:
        data = bedrock_service.parse_json_response(raw)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JD analysis response: {exc}",
        ) from exc

    # Normalise user_skills to a list of dicts regardless of the stored format.
    if isinstance(user_skills, dict):
        skills_list: list[dict] = [
            {"name": name, **attrs} if isinstance(attrs, dict) else {"name": name, "level": attrs}
            for name, attrs in user_skills.items()
        ]
    elif isinstance(user_skills, list):
        skills_list = user_skills
    else:
        skills_list = []

    data["user_skills"] = skills_list

    return JDAnalyzeResponse(**data)
