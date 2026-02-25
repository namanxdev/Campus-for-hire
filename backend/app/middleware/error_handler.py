"""Global error handling middleware for the Campus-to-Hire API."""

from __future__ import annotations

import logging
import traceback
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# Configure logging
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware.
    
    Catches all unhandled exceptions and returns a standardized error response.
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Log the error with full traceback
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_host": request.client.host if request.client else None,
                },
            )
            
            # Return standardized error response
            return self._create_error_response(exc, request)
    
    def _create_error_response(
        self, exc: Exception, request: Request
    ) -> JSONResponse:
        """Create a standardized error response."""
        
        error_detail = str(exc) if str(exc) else "An unexpected error occurred"
        
        # Determine status code based on exception type
        status_code = self._get_status_code(exc)
        
        # Build error response
        error_response: dict[str, Any] = {
            "success": False,
            "error": {
                "code": self._get_error_code(exc),
                "message": error_detail,
                "status_code": status_code,
            },
        }
        
        # Include traceback in debug mode (development only)
        # In production, don't expose internal details
        # Uncomment below for debug mode:
        # error_response["error"]["traceback"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )
    
    def _get_status_code(self, exc: Exception) -> int:
        """Determine HTTP status code based on exception type."""
        
        # Import common exception types
        from fastapi import HTTPException
        from sqlalchemy.exc import IntegrityError, OperationalError
        
        # FastAPI HTTP exceptions
        if isinstance(exc, HTTPException):
            return exc.status_code
        
        # Database errors
        if isinstance(exc, IntegrityError):
            return status.HTTP_409_CONFLICT
        
        if isinstance(exc, OperationalError):
            return status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Value errors
        if isinstance(exc, (ValueError, TypeError)):
            return status.HTTP_400_BAD_REQUEST
        
        # Authentication/Authorization errors
        error_name = exc.__class__.__name__.lower()
        if "auth" in error_name or "unauthorized" in error_name:
            return status.HTTP_401_UNAUTHORIZED
        if "permission" in error_name or "forbidden" in error_name:
            return status.HTTP_403_FORBIDDEN
        if "notfound" in error_name or "not found" in error_name:
            return status.HTTP_404_NOT_FOUND
        
        # Default to internal server error
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def _get_error_code(self, exc: Exception) -> str:
        """Generate a unique error code based on exception type."""
        
        exc_class = exc.__class__.__name__
        
        error_codes = {
            "HTTPException": "HTTP_ERROR",
            "IntegrityError": "DB_INTEGRITY_ERROR",
            "OperationalError": "DB_OPERATIONAL_ERROR",
            "ValueError": "VALIDATION_ERROR",
            "TypeError": "TYPE_ERROR",
            "KeyError": "MISSING_KEY_ERROR",
            "AttributeError": "ATTRIBUTE_ERROR",
            "IndexError": "INDEX_ERROR",
        }
        
        return error_codes.get(exc_class, "INTERNAL_SERVER_ERROR")


# Exception handler functions for direct use with FastAPI

async def http_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle HTTP exceptions."""
    from fastapi import HTTPException
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                },
            },
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle validation exceptions."""
    from fastapi.exceptions import RequestValidationError
    
    if isinstance(exc, RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "details": errors,
                },
            },
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        },
    )
