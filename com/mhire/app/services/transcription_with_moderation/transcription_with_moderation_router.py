from fastapi import APIRouter, HTTPException, status, File, UploadFile
import logging
import tempfile
import os
import time
from pathlib import Path

from com.mhire.app.services.transcription_with_moderation.transcription_with_moderation import (
    transcribe_and_moderate_audio
)
from com.mhire.app.services.transcription_with_moderation.transcription_with_moderation_schema import (
    TranscriptionWithModerationRequest, 
    TranscriptionWithModerationError
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/transcribe-moderate",
    tags=["transcription-moderation"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/ultra-fast",
    status_code=status.HTTP_200_OK,
    summary="Ultra-fast transcription with moderation",
    description="Fastest possible processing with aggressive caching and optimizations"
)
async def ultra_fast_transcribe_and_moderate(file: UploadFile = File(...)):
    """
    Ultra-fast transcription with moderation - optimized for speed.
    Uses all performance optimizations including caching and fast moderation.
    
    - **file**: Audio file to transcribe and moderate
    
    Returns minimal response for maximum speed.
    """
    temp_file_path = None
    start_time = time.time()
    
    try:
        # Minimal validation for speed
        if not file.filename or not Path(file.filename).suffix.lower() in {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}:
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Fast file handling
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix.lower()) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Ultra-fast processing
        request = TranscriptionWithModerationRequest(
            audio_file_path=temp_file_path,
            response_format="text",
            temperature=0
        )
        
        result = transcribe_and_moderate_audio(request)
        
        if isinstance(result, TranscriptionWithModerationError):
            raise HTTPException(status_code=400, detail="Processing failed")
        
        processing_time = time.time() - start_time
        
        # Minimal response for speed
        return {
            "transcript": result.transcript,
            "safe": result.is_safe,
            "flagged": result.moderation_flagged,
            "processing_time": round(processing_time, 3)
        }
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Processing failed")
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass