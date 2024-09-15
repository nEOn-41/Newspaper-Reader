# backend/app/utils/api_utils.py

from fastapi.responses import JSONResponse

def success_response(data, message="Operation successful"):
    return JSONResponse(content={"message": message, "data": data})

def error_response(detail, status_code=400):
    return JSONResponse(status_code=status_code, content={"error": detail})
