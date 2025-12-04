from fastapi import APIRouter, HTTPException, status, File, UploadFile
import logging
import tempfile
import os
from pathlib import Path

from com.mhire.app.services.transcription.transcription import transcribe_audio_file
from com.mhire.app.services.transcription.transcription_schema import (
    TranscriptionRequest, 
    TranscriptionError
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/transcribe",
    tags=["transcription"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/simple",
    status_code=status.HTTP_200_OK,
    summary="Simple audio transcription",
    description="Upload an audio file and get transcribed text with default settings"
)
async def simple_transcribe(file: UploadFile = File(...)):
    """
    Simple transcription endpoint - upload a file and get transcribed text with duration.
    
    - **file**: Audio file to transcribe
    
    Returns JSON response with transcribed text and audio duration in seconds.
    """
    temp_file_path = None
    
    try:
        logger.info(f"Simple transcription request for file: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Get file extension and validate
        file_extension = Path(file.filename).suffix.lower()
        supported_formats = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
        
        if file_extension not in supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Supported: {', '.join(supported_formats)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Create simple transcription request with accuracy-optimized defaults
        request = TranscriptionRequest(
            audio_file_path=temp_file_path,
            response_format="text",
            temperature=0,  # Most accurate setting
            prompt="This is a conversation from a dating app. Include proper punctuation and capitalization."
        )
        
        # Transcribe
        result = transcribe_audio_file(request)
        
        if isinstance(result, TranscriptionError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
        
        # Return both transcript and duration
        return {
            "transcript": result.transcript,
            "duration_seconds": result.duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in simple transcription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transcription failed"
        )
    
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {str(e)}")