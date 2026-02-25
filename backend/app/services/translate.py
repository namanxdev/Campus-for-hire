"""
Translation Service using Amazon Translate.
Provides text translation with support for Hindi, Tamil, and Telugu.
"""

import logging
from typing import List

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class TranslateService:
    """Service for translating text using Amazon Translate."""
    
    # Supported language codes
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "ur": "Urdu"
    }
    
    # Maximum text length for single translation (Amazon Translate limit)
    MAX_TEXT_LENGTH = 5000
    
    def __init__(self) -> None:
        self._client = boto3.client(
            "translate",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language code is supported.
        
        Args:
            language_code: ISO language code
            
        Returns:
            True if supported
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_supported_languages(self) -> dict:
        """
        Get list of supported languages.
        
        Returns:
            Dictionary of supported languages
        """
        return {
            "languages": [
                {"code": code, "name": name}
                for code, name in self.SUPPORTED_LANGUAGES.items()
            ]
        }
    
    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
    ) -> dict:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code (hi, ta, te, etc.)
            source_language: Source language code (default: en)
            
        Returns:
            Dictionary with translated text and metadata
            
        Raises:
            HTTPException: If translation fails
            ValueError: If language codes are invalid
        """
        # Validate inputs
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        if not self.is_language_supported(target_language):
            raise ValueError(f"Unsupported target language: {target_language}")
        
        if not self.is_language_supported(source_language):
            raise ValueError(f"Unsupported source language: {source_language}")
        
        # Handle long text by truncating (with warning)
        original_length = len(text)
        if original_length > self.MAX_TEXT_LENGTH:
            logger.warning(f"Text too long ({original_length} chars), truncating to {self.MAX_TEXT_LENGTH}")
            text = text[:self.MAX_TEXT_LENGTH]
        
        try:
            response = self._client.translate_text(
                Text=text,
                SourceLanguageCode=source_language,
                TargetLanguageCode=target_language,
            )
            
            return {
                "translated_text": response["TranslatedText"],
                "source_language": source_language,
                "target_language": target_language,
                "source_text_length": original_length,
                "translated": True
            }
            
        except ClientError as exc:
            error_code = exc.response.get('Error', {}).get('Code', 'Unknown')
            error_message = exc.response.get('Error', {}).get('Message', str(exc))
            
            logger.error(
                "Amazon Translate ClientError [%s -> %s]: %s - %s",
                source_language, target_language, error_code, error_message
            )
            
            # Handle specific error codes
            if error_code == 'UnsupportedLanguagePairException':
                raise HTTPException(
                    status_code=400,
                    detail=f"Translation from {source_language} to {target_language} is not supported"
                ) from exc
            elif error_code == 'TextSizeLimitExceededException':
                raise HTTPException(
                    status_code=400,
                    detail=f"Text size exceeds limit of {self.MAX_TEXT_LENGTH} characters"
                ) from exc
            elif error_code == 'ServiceUnavailableException':
                raise HTTPException(
                    status_code=503,
                    detail="Translation service temporarily unavailable"
                ) from exc
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Translation failed: {error_message}"
                ) from exc
                
        except BotoCoreError as exc:
            logger.error(
                "Amazon Translate BotoCoreError [%s -> %s]: %s",
                source_language, target_language, exc
            )
            raise HTTPException(
                status_code=503,
                detail="Translation service connection error"
            ) from exc
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: str = "en",
    ) -> List[dict]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (default: en)
            
        Returns:
            List of translation results
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            try:
                result = self.translate_text(text, target_language, source_language)
                results.append(result)
            except Exception as exc:
                logger.error(f"Failed to translate text in batch: {exc}")
                results.append({
                    "translated_text": text,  # Return original on failure
                    "source_language": source_language,
                    "target_language": target_language,
                    "translated": False,
                    "error": str(exc)
                })
        
        return results
    
    def detect_and_translate(
        self,
        text: str,
        target_language: str,
    ) -> dict:
        """
        Auto-detect source language and translate.
        Note: Amazon Translate requires explicit source language, 
        so this uses 'auto' which may not work with all language pairs.
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translation result with detected source language
        """
        try:
            response = self._client.translate_text(
                Text=text,
                SourceLanguageCode="auto",
                TargetLanguageCode=target_language,
            )
            
            return {
                "translated_text": response["TranslatedText"],
                "detected_source_language": response.get("SourceLanguageCode", "unknown"),
                "target_language": target_language,
                "translated": True
            }
            
        except Exception as exc:
            logger.error(f"Auto-detection translation failed: {exc}")
            raise HTTPException(
                status_code=500,
                detail=f"Translation with auto-detection failed: {exc}"
            ) from exc
    
    def translate_with_fallback(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
    ) -> dict:
        """
        Translate with fallback to original text if translation fails.
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language
            
        Returns:
            Translation result or original text with error info
        """
        try:
            return self.translate_text(text, target_language, source_language)
        except Exception as exc:
            logger.warning(f"Translation failed, returning original: {exc}")
            return {
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "translated": False,
                "error": str(exc)
            }
    
    def health_check(self) -> dict:
        """
        Perform a health check on the translation service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple translation to check connectivity
            response = self._client.translate_text(
                Text="Hello",
                SourceLanguageCode="en",
                TargetLanguageCode="hi"
            )
            return {
                "status": "healthy",
                "service": "Amazon Translate",
                "region": settings.AWS_REGION,
                "response_received": True
            }
        except Exception as exc:
            logger.error(f"Translate health check failed: {exc}")
            return {
                "status": "unhealthy",
                "service": "Amazon Translate",
                "region": settings.AWS_REGION,
                "error": str(exc)
            }


# Global instance
translate_service = TranslateService()
