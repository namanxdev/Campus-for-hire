from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import User
from app.schemas import TranslateRequest, TranslateResponse
from app.services.translate import translate_service

router = APIRouter(prefix="/api/translate", tags=["translate"])


@router.post("", response_model=TranslateResponse)
def translate_text(
    body: TranslateRequest,
    current_user: User = Depends(get_current_user),
) -> TranslateResponse:
    """Translate the provided text into the requested target language."""
    result = translate_service.translate_text(body.text, body.target_language)
    return TranslateResponse(**result)
