"""
FastAPI Application Entry Point
Optimized for performance with minimal overhead.
"""
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.restaurants import router as restaurants_router
from app.api.v1.admin import router as admin_router
from app.api.v1.orders import router as orders_router
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
# In development, allow all origins for Flutter web debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler - DEBUG modunda detaylı hata döndür
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Yakalanmamış hataları logla ve DEBUG modunda detay döndür."""
    tb = traceback.format_exc()
    logger.exception("Unhandled exception: %s", exc)
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "traceback": tb.split("\n"),
            },
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


# Include Routers
app.include_router(auth_router, prefix="/v1")
app.include_router(restaurants_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")
app.include_router(orders_router, prefix="/v1")


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
