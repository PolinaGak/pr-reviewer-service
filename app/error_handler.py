from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .schemas.error import ErrorResponse, ErrorDetail, ErrorCode


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    code = ErrorCode.INTERNAL

    if exc.status_code == 404:
        code = ErrorCode.NOT_FOUND
    elif exc.status_code == 400:
        code = ErrorCode.BAD_REQUEST
    elif exc.status_code == 422:
        code = ErrorCode.VALIDATION_ERROR

    response = ErrorResponse(error=ErrorDetail(code=code, message=str(exc.detail)))
    return JSONResponse(status_code=exc.status_code, content=response.dict())
