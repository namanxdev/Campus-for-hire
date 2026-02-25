"""
Bedrock Service for AI model invocations.
Provides retry logic, error handling, and streaming support.
"""

import json
import logging
import random
import re
import time
from typing import AsyncGenerator

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class BedrockError(Exception):
    """Base exception for Bedrock service errors."""
    pass


class BedrockRateLimitError(BedrockError):
    """Raised when rate limit is exceeded."""
    pass


class BedrockTokenLimitError(BedrockError):
    """Raised when token limit is exceeded."""
    pass


class BedrockContentFilterError(BedrockError):
    """Raised when content is filtered."""
    pass


class BedrockServiceUnavailableError(BedrockError):
    """Raised when Bedrock service is unavailable."""
    pass


class BedrockValidationError(BedrockError):
    """Raised when request validation fails."""
    pass


class BedrockService:
    """Service for invoking Amazon Bedrock models with retry logic and comprehensive error handling."""
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # seconds
    MAX_DELAY = 30.0  # seconds
    JITTER_FACTOR = 0.1  # 10% jitter
    
    # Default fallback responses for different use cases
    FALLBACK_RESPONSES = {
        "roadmap": '{"title": "Learning Roadmap", "total_weeks": 8, "weeks": [], "fallback": true, "message": "We\'re experiencing high demand. Please try again later for a personalized roadmap."}',
        "interview": "I apologize, but I'm having trouble processing your response right now. Please try again in a moment. Your preparation is still valuable!",
        "jd_analysis": '{"role": "Unknown", "company": null, "required_skills": [], "gap_analysis": [], "recommendations": ["Please try again later for detailed analysis"], "fallback": true}',
        "explanation": '{"concept": "Unknown", "explanation": {"simple_definition": "Unable to explain at this time", "detailed_explanation": "We\'re experiencing technical difficulties. Please try again or check GeeksforGeeks for this topic."}, "fallback": true}',
        "skill_assessment": '{"assessment_id": "fallback", "skill_area": "unknown", "questions": [], "fallback": true, "message": "Assessment generation failed. Please try again."}',
        "weekly_checkin": '{"week": 0, "progress_assessment": "unknown", "acknowledgment": "We couldn\'t process your check-in. Please try again.", "fallback": true}',
        "resume_tips": '{"overall_score": 0, "ats_friendly": false, "sections": {}, "fallback": true, "message": "Resume analysis temporarily unavailable. Please try again."}',
        "resource_recommendations": '{"topic": "unknown", "resources": [], "fallback": true, "message": "Resource recommendations temporarily unavailable."}',
        "translation": '{"translated": false, "fallback": true, "message": "Translation service temporarily unavailable."}',
        "default": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    }
    
    def __init__(self) -> None:
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self._model_id = settings.BEDROCK_MODEL_ID
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Formula: min(BASE_DELAY * 2^attempt, MAX_DELAY) + random_jitter
        """
        exponential_delay = self.BASE_DELAY * (2 ** attempt)
        capped_delay = min(exponential_delay, self.MAX_DELAY)
        jitter = capped_delay * self.JITTER_FACTOR * random.uniform(-1, 1)
        return max(0.1, capped_delay + jitter)
    
    def _classify_error(self, error: Exception) -> tuple[bool, bool, str]:
        """
        Classify an error as retryable and/or fallback-worthy.
        
        Returns:
            Tuple of (is_retryable, should_fallback, error_type)
        """
        error_message = str(error).lower()
        error_type = "unknown"
        
        # Rate limit errors - retryable with backoff
        if any(x in error_message for x in ["rate limit", "throttling", "too many requests", "throttlingexception"]):
            error_type = "rate_limit"
            return True, False, error_type
        
        # Token limit errors - not retryable, use fallback
        if any(x in error_message for x in ["token limit", "too large", "context length", "validationexception"]):
            error_type = "token_limit"
            return False, True, error_type
        
        # Content filter errors - not retryable, use fallback
        if any(x in error_message for x in ["content filter", "blocked", "safety", "access denied"]):
            error_type = "content_filter"
            return False, True, error_type
        
        # Service unavailable - retryable
        if any(x in error_message for x in ["service unavailable", "internal error", "serviceexception"]):
            error_type = "service_unavailable"
            return True, False, error_type
        
        # Timeout errors - retryable
        if any(x in error_message for x in ["timeout", "timed out", "connection"]):
            error_type = "timeout"
            return True, False, error_type
        
        # Check BotoCore/ClientError for specific error codes
        if isinstance(error, ClientError):
            error_code = error.response.get('Error', {}).get('Code', '')
            if error_code in ['ThrottlingException', 'ServiceUnavailable']:
                error_type = "aws_retryable"
                return True, False, error_type
            elif error_code in ['ValidationException', 'AccessDeniedException', 'ResourceNotFoundException']:
                error_type = "aws_client_error"
                return False, True, error_type
        
        # BotoCore errors - may be retryable
        if isinstance(error, BotoCoreError):
            error_type = "boto_core"
            return True, True, error_type
        
        # JSON decode errors - not retryable, use fallback
        if isinstance(error, json.JSONDecodeError):
            error_type = "json_decode"
            return False, True, error_type
        
        # Default: try once more then fallback
        error_type = "unknown_retryable"
        return True, True, error_type
    
    def _get_fallback_response(self, fallback_type: str, error_info: dict = None) -> str:
        """
        Get an appropriate fallback response.
        
        Args:
            fallback_type: Type of fallback response
            error_info: Additional error information to include
            
        Returns:
            Fallback response string
        """
        fallback = self.FALLBACK_RESPONSES.get(fallback_type, self.FALLBACK_RESPONSES["default"])
        
        # Try to parse and add error info if JSON
        try:
            fallback_dict = json.loads(fallback)
            if error_info:
                fallback_dict["error_info"] = error_info
            return json.dumps(fallback_dict)
        except (json.JSONDecodeError, TypeError):
            return fallback
    
    def invoke_model(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        fallback_type: str = "default",
    ) -> str:
        """
        Invoke Bedrock model with retry logic and fallback handling.
        
        Args:
            system_prompt: System context/persona
            user_prompt: User message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            fallback_type: Type of fallback response if all retries fail
            
        Returns:
            Model response text
            
        Raises:
            HTTPException: If all retries are exhausted and no fallback available
        """
        # Validate inputs before sending
        is_valid, error_msg = self.validate_prompt_inputs(system_prompt, user_prompt, max_tokens)
        if not is_valid:
            logger.error(f"Invalid prompt inputs: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        
        last_error = None
        error_type = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Invoking Bedrock model (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                response = self._client.invoke_model(
                    modelId=self._model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(body),
                )
                
                response_body = json.loads(response["body"].read())
                content = response_body["content"][0]["text"]
                
                logger.info(f"Bedrock invocation successful on attempt {attempt + 1}")
                return content
                
            except Exception as exc:
                last_error = exc
                is_retryable, should_fallback, error_type = self._classify_error(exc)
                
                logger.warning(
                    f"Attempt {attempt + 1} failed with {error_type}: {exc}"
                )
                
                if not is_retryable:
                    logger.error(f"Non-retryable error ({error_type}): {exc}")
                    break
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.MAX_RETRIES} attempts exhausted")
        
        # Return fallback response instead of raising
        error_info = {
            "error_type": error_type,
            "error_message": str(last_error),
            "retries_exhausted": True
        }
        
        if fallback_type in self.FALLBACK_RESPONSES:
            logger.warning(f"Returning fallback response for {fallback_type}")
            return self._get_fallback_response(fallback_type, error_info)
        
        # If no fallback defined, raise the error
        raise HTTPException(
            status_code=503,
            detail=f"Bedrock service unavailable after {self.MAX_RETRIES} attempts: {last_error}",
        ) from last_error
    
    def invoke_model_with_history(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        fallback_type: str = "default",
    ) -> str:
        """
        Invoke Bedrock model with conversation history and retry logic.
        
        Args:
            system_prompt: System context/persona
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            fallback_type: Type of fallback response if all retries fail
            
        Returns:
            Model response text
        """
        # Validate inputs
        if not messages or not isinstance(messages, list):
            raise HTTPException(status_code=400, detail="Messages must be a non-empty list")
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": messages,
        }
        
        last_error = None
        error_type = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Invoking Bedrock with history (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                response = self._client.invoke_model(
                    modelId=self._model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(body),
                )
                
                response_body = json.loads(response["body"].read())
                content = response_body["content"][0]["text"]
                
                logger.info(f"Bedrock invocation with history successful on attempt {attempt + 1}")
                return content
                
            except Exception as exc:
                last_error = exc
                is_retryable, _, error_type = self._classify_error(exc)
                
                if not is_retryable or attempt >= self.MAX_RETRIES - 1:
                    break
                
                delay = self._calculate_delay(attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {exc}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
        
        # Return fallback response
        error_info = {
            "error_type": error_type,
            "error_message": str(last_error),
            "retries_exhausted": True
        }
        
        if fallback_type in self.FALLBACK_RESPONSES:
            logger.warning(f"Returning fallback response for {fallback_type}")
            return self._get_fallback_response(fallback_type, error_info)
        
        raise HTTPException(
            status_code=503,
            detail=f"Bedrock invocation failed after {self.MAX_RETRIES} attempts: {last_error}",
        ) from last_error
    
    async def generate_streaming_response(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the model.
        
        Args:
            system_prompt: System context/persona
            user_prompt: User message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Yields:
            Chunks of the response as they're generated
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        
        try:
            response = self._client.invoke_model_with_response_stream(
                modelId=self._model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )
            
            # Process the streaming response
            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {})
                    if "text" in delta:
                        yield delta["text"]
                        
                elif chunk.get("type") == "message_stop":
                    break
                    
        except Exception as exc:
            logger.error(f"Streaming response failed: {exc}")
            error_type, _, _ = self._classify_error(exc)
            yield f"\n\n[Error: Service temporarily unavailable ({error_type}). Please try again.]"
    
    def invoke_model_simple(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """
        Simple model invocation without system prompt.
        
        Args:
            prompt: The complete prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Model response text
        """
        return self.invoke_model(
            system_prompt="You are a helpful assistant.",
            user_prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    
    def parse_json_response(self, response: str) -> dict:
        """
        Parse JSON from model response, handling markdown code blocks.
        
        Args:
            response: Raw model response
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            json.JSONDecodeError: If response cannot be parsed
        """
        if not response or not isinstance(response, str):
            raise json.JSONDecodeError("Empty or invalid response", "", 0)
        
        # Try to find JSON in markdown code blocks
        match = re.search(
            r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", response, re.DOTALL
        )
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON without markdown
        match = re.search(r"(\{.*\}|\[.*\])", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try parsing the entire response
        return json.loads(response)
    
    def parse_json_response_safe(
        self,
        response: str,
        fallback: dict | None = None
    ) -> dict:
        """
        Safely parse JSON response with fallback.
        
        Args:
            response: Raw model response
            fallback: Fallback dictionary if parsing fails
            
        Returns:
            Parsed JSON or fallback
        """
        try:
            return self.parse_json_response(response)
        except json.JSONDecodeError as exc:
            logger.warning(f"Failed to parse JSON response: {exc}")
            return fallback or {
                "error": "Failed to parse response",
                "raw_response": response[:500] if response else None,
                "fallback": True
            }
    
    def validate_prompt_inputs(
        self,
        system_prompt: str | None,
        user_prompt: str,
        max_tokens: int,
    ) -> tuple[bool, str]:
        """
        Validate prompt inputs before sending to model.
        
        Args:
            system_prompt: System prompt text
            user_prompt: User prompt text
            max_tokens: Max tokens setting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not user_prompt or not isinstance(user_prompt, str) or not user_prompt.strip():
            return False, "User prompt cannot be empty"
        
        if len(user_prompt) > 100000:  # ~25k tokens limit (rough estimate)
            return False, "User prompt too long (max ~25k tokens). Please shorten your request."
        
        if system_prompt and len(system_prompt) > 10000:
            return False, "System prompt too long (max ~2.5k tokens)"
        
        if max_tokens < 1 or max_tokens > 4096:
            return False, "max_tokens must be between 1 and 4096"
        
        return True, ""
    
    def health_check(self) -> dict:
        """
        Perform a health check on the Bedrock service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple invocation to check connectivity
            response = self._client.invoke_model(
                modelId=self._model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "temperature": 0.0,
                    "messages": [{"role": "user", "content": "Hi"}],
                }),
            )
            return {
                "status": "healthy",
                "model_id": self._model_id,
                "region": settings.AWS_REGION,
                "response_received": True
            }
        except Exception as exc:
            logger.error(f"Bedrock health check failed: {exc}")
            return {
                "status": "unhealthy",
                "model_id": self._model_id,
                "region": settings.AWS_REGION,
                "error": str(exc),
                "error_type": "connection_error"
            }


# Global instance
bedrock_service = BedrockService()
