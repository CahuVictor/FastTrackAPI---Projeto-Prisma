# app/utils/http.py
from fastapi import HTTPException

def raise_http(log_func, status_code, detail, **log_data):
    log_func(detail, **log_data)
    raise HTTPException(status_code=status_code, detail=detail)
