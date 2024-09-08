from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, query, delete
from utils.utils import load_metadata
from config import LOGGING_CONFIG
import logging
from logging.config import dictConfig

# Configure logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(delete.router)

@app.on_event("startup")
async def startup_event():
    # Load existing metadata on startup
    load_metadata()
    logger.info("Application started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)