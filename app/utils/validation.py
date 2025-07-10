# app/utils/validation.py
from fastapi import HTTPException

def validate_not_empty(payload, msg: str, logger=None, **log_data):  # TODO Função criada mas não utilizada, no código o raise está mais descritivo, ver como ajustar para utilizar essa função
    """
    Raises an HTTPException (400) if the payload is None or contains no meaningful fields.

    Optionally logs a warning before raising.

    Args:
        payload: The data (dict or object) to validate.
        msg (str): The error message for the HTTPException.
        logger (structlog.BoundLogger, optional): Logger to use for warnings.
        **log_data: Additional keyword arguments for logging.

    Raises:
        HTTPException: If payload is empty or None.

    Example:
        validate_not_empty(update.model_dump(exclude_unset=True), "No valid fields for update", logger=logger, event_id=42)
    """
    if payload is None or (isinstance(payload, dict) and not any(payload.values())):
        if logger:
            logger.warning(msg, **log_data)
        raise HTTPException(400, msg)