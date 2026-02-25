import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Interview
from app.schemas import InterviewStartRequest, InterviewRespondRequest, InterviewResponse
from app.services.bedrock import bedrock_service
from app.services.prompts import (
    INTERVIEW_SYSTEM_PROMPT,
    get_interview_start_prompt,
    get_interview_evaluate_prompt,
)

router = APIRouter(prefix="/api/interview", tags=["interview"])


def _evaluate_interview(interview: Interview) -> tuple[float | None, str | None]:
    """
    Call Bedrock to evaluate the completed interview.

    Returns a (score, feedback) tuple parsed from the JSON response.
    On any parsing failure the raw text is returned as feedback with no score.
    """
    raw = bedrock_service.invoke_model(
        INTERVIEW_SYSTEM_PROMPT,
        get_interview_evaluate_prompt(
            interview.role,
            interview.company,
            interview.messages,
        ),
    )

    try:
        data = json.loads(raw)
        score = data.get("score")
        feedback = data.get("feedback")
    except (json.JSONDecodeError, AttributeError):
        score = None
        feedback = raw

    return score, feedback


@router.post("/start", response_model=InterviewResponse)
def start_interview(
    body: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewResponse:
    """Start a new mock interview session and return the first question."""
    first_question = bedrock_service.invoke_model(
        INTERVIEW_SYSTEM_PROMPT,
        get_interview_start_prompt(body.role, body.company),
    )

    interview = Interview(
        user_id=current_user.id,
        role=body.role,
        company=body.company,
        messages=[{"role": "assistant", "content": first_question}],
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    return interview


@router.post("/respond", response_model=InterviewResponse)
def respond_to_interview(
    body: InterviewRespondRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewResponse:
    """
    Send a candidate answer to an ongoing interview.

    After 5 Q&A pairs (10 messages total) the interview is automatically
    evaluated and the session is closed with a score and feedback.
    """
    interview = (
        db.query(Interview)
        .filter(Interview.id == body.interview_id, Interview.user_id == current_user.id)
        .first()
    )

    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Append the candidate's answer.
    messages = list(interview.messages)
    messages.append({"role": "user", "content": body.message})
    interview.messages = messages

    # Auto-evaluate when 5 Q&A pairs (10 messages) have been exchanged.
    if len(messages) >= 10:
        score, feedback = _evaluate_interview(interview)
        interview.score = score
        interview.feedback = feedback
        db.commit()
        db.refresh(interview)
        return interview

    # Otherwise ask the next interview question.
    ai_response = bedrock_service.invoke_model_with_history(
        INTERVIEW_SYSTEM_PROMPT,
        messages,
    )

    messages.append({"role": "assistant", "content": ai_response})
    interview.messages = messages

    db.commit()
    db.refresh(interview)

    return interview


@router.post("/{interview_id}/end", response_model=InterviewResponse)
def end_interview(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewResponse:
    """Manually end an interview and receive a score with detailed feedback."""
    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .first()
    )

    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    score, feedback = _evaluate_interview(interview)
    interview.score = score
    interview.feedback = feedback

    db.commit()
    db.refresh(interview)

    return interview


@router.get("/history", response_model=list[InterviewResponse])
def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InterviewResponse]:
    """Return all past interviews for the current user, newest first."""
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )

    return interviews
