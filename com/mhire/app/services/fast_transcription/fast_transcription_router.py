from fastapi import APIRouter, HTTPException, status, File, UploadFile
import logging
import tempfile
import os
import time
from pathlib import Path

from com.mhire.app.services.fast_transcription.fast_transcription import transcribe_audio
from com.mhire.app.services.fast_transcription.fast_transcription_schema import (
    TranscriptionRequest, 
    TranscriptionError
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/transcribe",
    tags=["transcription-moderation"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/ultra-fast",
    status_code=status.HTTP_200_OK,
    summary="Ultra-fast transcription",
    description="Fastest possible transcription processing without moderation"
)
async def ultra_fast_transcribe(file: UploadFile = File(...)):
    """
    Ultra-fast transcription - optimized for speed.
    Only performs transcription without any moderation checks.
    
    - **file**: Audio file to transcribe
    
    Returns transcript and processing time only.
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
        
        # Transcription only - no moderation
        request = TranscriptionRequest(
            audio_file_path=temp_file_path,
            response_format="text",
            temperature=0
        )
        
        result = transcribe_audio(request)
        
        if isinstance(result, TranscriptionError):
            raise HTTPException(status_code=400, detail="Transcription failed")
        
        processing_time = time.time() - start_time
        
        # Simple response with only transcript and processing time
        return {
            "transcript": result.transcript,
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