from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse

from app.api.v1.router import router as api_router
from app.core.config import settings
from app.exceptions.core_exception import CoreError

load_dotenv()

app = FastAPI(
    title=settings.name,
    description="Hackathon backend based on FastAPI and Pydantic validation designed to ship fast, fast, fast 🏎️",
    version="0.1.0",
)

# Add CORS middleware to allow all origins and methods for local network access. Do not use outside hackathon projects or for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(CoreError)
async def error_handler(_: Request, exc: CoreError) -> JSONResponse:
    """
    Custom exception handler for BusinessLogicError.
    Converts the error into a structured JSON response.
    """
    # Map specific exceptions to status codes
    status_codes = {
        "TaskNotFoundError": 404,
        "TaskInitalizationError": 500,
    }

    # Default to 400 if not specified
    status_code = status_codes.get(exc.__class__.__name__, 400)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "code": exc.code,
            "details": exc.details or {},
        },
    )
