"""
Standardized API Response Utilities

Provides consistent response formatting across all API endpoints.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response structure."""

    success: bool = True
    message: str
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Standard error response structure."""

    success: bool = False
    message: str
    errors: Optional[List[Dict[str, Any]]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata structure."""

    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response structure."""

    success: bool = True
    message: str = "Data retrieved successfully"
    data: List[T]
    meta: PaginationMeta


def success_response(
    data: Any = None,
    message: str = "Success",
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: The response data payload
        message: Human-readable success message

    Returns:
        Dict with standardized success response format

    Example:
        >>> success_response(data={"user_id": "123"}, message="User created")
        {
            "success": True,
            "message": "User created",
            "data": {"user_id": "123"}
        }
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    errors: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        message: Human-readable error message
        status_code: HTTP status code (included in response for reference)
        errors: Optional list of detailed error objects

    Returns:
        Dict with standardized error response format

    Example:
        >>> error_response(message="Validation failed", errors=[{"field": "email", "message": "Invalid email"}])
        {
            "success": False,
            "message": "Validation failed",
            "errors": [{"field": "email", "message": "Invalid email"}]
        }
    """
    response: Dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if errors:
        response["errors"] = errors
    return response


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    per_page: int,
    message: str = "Data retrieved successfully",
) -> Dict[str, Any]:
    """
    Create a standardized paginated response.

    Args:
        data: List of items for current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        per_page: Number of items per page
        message: Human-readable success message

    Returns:
        Dict with standardized paginated response format including metadata

    Example:
        >>> paginated_response(data=[{"id": 1}], total=100, page=1, per_page=10)
        {
            "success": True,
            "message": "Data retrieved successfully",
            "data": [{"id": 1}],
            "meta": {
                "total": 100,
                "page": 1,
                "per_page": 10,
                "total_pages": 10,
                "has_next": True,
                "has_prev": False
            }
        }
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
