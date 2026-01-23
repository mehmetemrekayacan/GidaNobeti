"""
FastAPI Application Entry Point
Optimized for performance with minimal overhead.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.db.session import engine
import logging

logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,  # Disable in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# CORS Middleware (optimized)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Include Routers
app.include_router(auth_router, prefix="/v1")


# Health Check Endpoint (minimal overhead)
@app.get("/health", tags=["Health"], response_class=JSONResponse)
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns: Service status and version.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Gıda Nöbeti API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
    }


# Startup Event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔍 Debug Mode: {settings.DEBUG}")
    
    # Test database connection
    try:
        from app.db.models.base import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database connection successful and tables created/verified")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {str(e)}")
        logger.warning(f"Database initialization: {str(e)}")


# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    print(f"👋 {settings.APP_NAME} shutting down...")
