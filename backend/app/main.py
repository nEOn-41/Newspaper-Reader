from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import upload, query, delete, clients, pdfs
from .utils.general_utils import load_metadata
from .config import LOGGING_CONFIG
from .utils.custom_exceptions import (
    PDFUploadError,
    PDFProcessingError,
    ClientManagementError,
    QueryProcessingError,
    ResourceNotFoundError,
    InvalidJSONError,
    RateLimitExceededError
)
from .models.system_prompt import save_system_prompt, get_system_prompt, get_additional_query
import asyncio
from .utils.request_pipeline import request_worker
from .utils.request_pipeline_pro import request_worker_pro
import logging
from logging.config import dictConfig
from typing import Dict

# Configure logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(delete.router)
app.include_router(clients.router)
app.include_router(pdfs.router)

@app.exception_handler(PDFUploadError)
@app.exception_handler(PDFProcessingError)
@app.exception_handler(ClientManagementError)
@app.exception_handler(QueryProcessingError)
@app.exception_handler(ResourceNotFoundError)
@app.exception_handler(InvalidJSONError)
@app.exception_handler(RateLimitExceededError)
async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for custom exceptions.
    """
    logger.error(f"Custom exception occurred: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again later."},
    )

@app.on_event("startup")
async def startup_event() -> None:
    """
    Startup event handler for the FastAPI application.
    """
    # Load existing metadata on startup
    load_metadata()
    logger.info("Application started")
    # Start the request workers
    asyncio.create_task(request_worker())       # For gemini-1.5-flash
    asyncio.create_task(request_worker_pro())   # For gemini-1.5-pro-latest

@app.get("/system-prompt")
async def get_system_prompt_route() -> Dict[str, str]:
    """
    Endpoint to retrieve the current system prompt and additional query.

    Returns:
        Dict[str, str]: A dictionary containing the system prompt and additional query.
    """
    system_prompt = get_system_prompt()
    additional_query = get_additional_query()
    return {"system_prompt": system_prompt, "additional_query": additional_query}

@app.post("/system-prompt")
async def update_system_prompt_route(data: Dict[str, str]) -> Dict[str, str]:
    """
    Endpoint to update the system prompt and additional query.

    Args:
        data (Dict[str, str]): A dictionary containing the new system prompt and additional query.

    Returns:
        Dict[str, str]: A dictionary with a success message.
    """
    save_system_prompt(data.get('system_prompt', ''), data.get('additional_query', ''))
    return {"message": "System prompt and additional query updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)