from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.config.settings import settings
from backend.app.database.connection import init_db
from backend.app.logging.logger import logger
from backend.app.logging.middleware import LoggingMiddleware, request_id_ctx
from backend.app.routes.feedback import router as feedback_router
from backend.app.schemas.common import APIResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.exception("Failed to initialize database.")
        raise e
    yield

app = FastAPI(
    title="Sentiment Analysis Service",
    description="A FastAPI REST API offering sentiment-analysis utilizing spaCy en_core_web_sm.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured Request Logging Middleware
app.add_middleware(LoggingMiddleware)

# Register routers
app.include_router(feedback_router)

# --- Global Exception Handlers for Standard Envelope Format ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles request validation errors (Pydantic validation, missing fields, type errors).
    """
    errors = exc.errors()
    details = []
    for err in errors:
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        details.append(f"[{loc}]: {msg}")
    
    error_msg = "Validation failed: " + "; ".join(details)
    
    response_body = APIResponse(
        success=False,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request input validation failed.",
        error_message=error_msg,
        data=None
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_body.model_dump()
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handles standard HTTP exceptions raised inside endpoints (e.g. 401 Unauthorized, 404 Not Found).
    """
    response_body = APIResponse(
        success=False,
        status_code=exc.status_code,
        message="An API request error occurred.",
        error_message=str(exc.detail),
        data=None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_body.model_dump(),
        headers=getattr(exc, "headers", None)
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for database errors or general server failures.
    """
    current_request_id = request_id_ctx.get()
    logger.exception(
        f"Unhandled server error: {str(exc)}",
        extra={"request_id": current_request_id}
    )
    
    response_body = APIResponse(
        success=False,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected server error occurred.",
        error_message=str(exc),
        data=None
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_body.model_dump()
    )

@app.get("/health", tags=["System"])
def health_check():
    """
    Liveness probe endpoint.
    """
    return {"status": "healthy", "service": "sentiment-analysis-backend"}
