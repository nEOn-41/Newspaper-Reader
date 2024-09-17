from fastapi.responses import JSONResponse
from typing import Any

def success_response(data: Any, message: str = "Operation successful") -> JSONResponse:
    """
    Creates a standardized success response.

    Args:
        data (Any): The data to be included in the response.
        message (str, optional): A success message. Defaults to "Operation successful".

    Returns:
        JSONResponse: A FastAPI JSONResponse object with the success data and message.
    """
    return JSONResponse(content={"message": message, "data": data})

def error_response(detail: str, status_code: int = 400) -> JSONResponse:
    """
    Creates a standardized error response.

    Args:
        detail (str): The error detail message.
        status_code (int, optional): The HTTP status code. Defaults to 400.

    Returns:
        JSONResponse: A FastAPI JSONResponse object with the error details and status code.
    """
    return JSONResponse(status_code=status_code, content={"error": detail})