# custom_exceptions.py

from fastapi import HTTPException

class PDFUploadError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"PDF Upload Error: {detail}")

class PDFProcessingError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"PDF Processing Error: {detail}")

class ClientManagementError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Client Management Error: {detail}")

class QueryProcessingError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Query Processing Error: {detail}")

class ResourceNotFoundError(HTTPException):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(status_code=404, detail=f"{resource_type} not found: {resource_id}")

class InvalidJSONError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Invalid JSON Error: {detail}")

class RateLimitExceededError(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail="Rate limit exceeded. Please try again later.")