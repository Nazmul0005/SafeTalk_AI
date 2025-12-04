from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from com.mhire.app.services.moderation.moderation_router import router as detection_router
from com.mhire.app.services.transcription.transcription_router import router as transcription_router
from com.mhire.app.services.transcription_with_moderation.transcription_with_moderation_router import router as transcription_moderation_router
from com.mhire.app.services.fast_transcription.fast_transcription_router import router as fast_transcription_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MHire Content Moderation API",
    description="API for content moderation in dating applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Include the fast transcription router
app.include_router(fast_transcription_router)

# Include the detection router
app.include_router(detection_router)

# Include the transcription router
app.include_router(transcription_router)

# Include the transcription with moderation router
app.include_router(transcription_moderation_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MHire Content Moderation & Transcription API",
        "version": "1.0.0",
        "available_endpoints": {
            "fast_transcription": "/transcribe-moderate/ultra-fast",
            "moderation": "/moderation/moderate-text",
            "simple_transcription": "/transcribe/simple", 
            "ultra_fast_transcription_with_moderation": "/transcribe-moderate/ultra-fast"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health():
    """General health check"""
    return {
        "status": "healthy",
        "app": "mhire-api",
        "active_services": ["moderation", "transcription", "transcription-with-moderation"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )