"""
FastAPI Main Application
Exposes all educational AI functionality via REST API
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn


from app.core.logging_config import setup_logging, get_logger
from app.core.config import settings, ensure_directories
from app.core.health_check import get_system_health
from app.core.exceptions import BaseAppException

# Import services
from app.services.llm_service import get_llm_service, close_llm_service


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting AI Educational System...")
    
    # Setup logging
    setup_logging(
        log_level=settings.LOG_LEVEL.value,
        json_output=settings.LOG_JSON_FORMAT
    )
    
    # Ensure directories exist
    ensure_directories()
    
    # Initialize services
    try:
        llm = await get_llm_service()
        await llm.check_model_availability()
        logger.info("✅ LLM service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM: {e}")
    
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Educational System...")
    await close_llm_service()
    logger.info("✅ Application shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered educational document reasoning system with semantic evaluation",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(BaseAppException)
async def custom_exception_handler(request, exc: BaseAppException):
    """Handle custom application exceptions"""
    logger.error(
        f"Application error: {exc.error_code.value} | {exc.message}",
        extra={"error_details": exc.details}
    )
    
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Comprehensive health check
    Returns status of all system components
    """
    health_status = await get_system_health()
    
    # Determine HTTP status code based on health
    if health_status["overall_status"] == "healthy":
        status_code = 200
    elif health_status["overall_status"] == "degraded":
        status_code = 200  # Still operational
    else:
        status_code = 503  # Service unavailable
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.get("/health/simple")
async def simple_health():
    """Simple health check for load balancers"""
    return {"status": "ok"}


# ============================================================================
# Import API Routers
# ============================================================================

# We'll create these router files next
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])


# ============================================================================
# Additional Utility Endpoints
# ============================================================================

@app.get("/api/config")
async def get_config():
    """Get public configuration"""
    return {
        "supported_formats": settings.get_supported_formats(),
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
        "chunk_size": settings.CHUNK_SIZE,
        "model": settings.OLLAMA_MODEL,
        "supported_intents": [
            "answer_generation",
            "answer_evaluation",
            "doubt_clarification",
            "question_generation"
        ]
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from app.services.vector_store_service import get_vector_store
    from app.services.embedding_service import get_embedding_service
    
    vector_store = get_vector_store()
    embedding_service = get_embedding_service()
    
    return {
        "vector_store": vector_store.get_stats(),
        "embedding_service": embedding_service.get_stats()
    }


# ============================================================================
# Static Frontend
# ============================================================================

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

@app.get("/app")
async def serve_frontend():
    """Serve the frontend application"""
    return FileResponse(STATIC_DIR / "index.html")

# Mount static files AFTER all API routes
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.value.lower()
    )
