# app/utils/http.py
from fastapi import HTTPException

def raise_http(log_func, status_code, detail, **log_data):
    """
    Logs an error or warning and raises a FastAPI HTTPException.

    Centralizes error reporting for consistent API responses.

    Args:
        log_func (Callable): Logger method to call (e.g., logger.warning, logger.error).
        status_code (int): HTTP status code for the response.
        detail (str): Error message for the client.
        **log_data: Extra data for the log entry.

    Raises:
        HTTPException: Always.

    Example:
        raise_http(logger.error, 404, "Resource not found", resource_id=42)
    """
    log_func(detail, **log_data)
    raise HTTPException(status_code=status_code, detail=detail)
