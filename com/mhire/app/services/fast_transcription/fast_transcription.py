import logging
import hashlib
import time
from typing import Union, Optional, Tuple
from functools import lru_cache
from pathlib import Path

from com.mhire.app.services.transcription.transcription import transcribe_audio_file
from com.mhire.app.services.transcription.transcription_schema import TranscriptionRequest, TranscriptionError
from com.mhire.app.services.fast_transcription.fast_transcription_schema import (
    TranscriptionRequest as LocalTranscriptionRequest,
    TranscriptionResponse,
    TranscriptionError as LocalTranscriptionError
)

logger = logging.getLogger(__name__)

# Performance optimizations
ENABLE_CACHING = True
CACHE_MAX_AGE = 3600  # 1 hour cache TTL
MAX_CACHE_SIZE = 1000

# Global caches
_transcription_cache = {}
_cache_timestamps = {}


@lru_cache(maxsize=MAX_CACHE_SIZE)
def _get_file_hash(file_path: str, file_size: int, file_mtime: float) -> str:
    """Generate a hash for file caching based on path, size, and modification time"""
    return hashlib.md5(f"{file_path}:{file_size}:{file_mtime}".encode()).hexdigest()


def _get_file_info(file_path: str) -> Tuple[int, float]:
    """Get file info for caching"""
    try:
        path = Path(file_path)
        stat = path.stat()
        return stat.st_size, stat.st_mtime
    except:
        return 0, 0


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cache entry is still valid"""
    if not ENABLE_CACHING:
        return False
    
    timestamp = _cache_timestamps.get(cache_key)
    if timestamp is None:
        return False
    
    return (time.time() - timestamp) < CACHE_MAX_AGE


def _get_cached_transcription(file_path: str, request_params: dict) -> Optional[dict]:
    """Get cached transcription result if available"""
    if not ENABLE_CACHING:
        return None
    
    try:
        file_size, file_mtime = _get_file_info(file_path)
        file_hash = _get_file_hash(file_path, file_size, file_mtime)
        
        # Create cache key including request parameters
        params_str = f"{request_params.get('language', '')}:{request_params.get('response_format', 'text')}:{request_params.get('temperature', 0)}"
        cache_key = f"transcription:{file_hash}:{params_str}"
        
        if _is_cache_valid(cache_key) and cache_key in _transcription_cache:
            logger.info(f"Cache hit for transcription: {file_path}")
            return _transcription_cache[cache_key]
    except Exception as e:
        logger.warning(f"Cache lookup failed: {e}")
    
    return None


def _cache_transcription(file_path: str, request_params: dict, result: dict):
    """Cache transcription result"""
    if not ENABLE_CACHING:
        return
    
    try:
        file_size, file_mtime = _get_file_info(file_path)
        file_hash = _get_file_hash(file_path, file_size, file_mtime)
        
        params_str = f"{request_params.get('language', '')}:{request_params.get('response_format', 'text')}:{request_params.get('temperature', 0)}"
        cache_key = f"transcription:{file_hash}:{params_str}"
        
        _transcription_cache[cache_key] = result
        _cache_timestamps[cache_key] = time.time()
        
        # Clean old cache entries if cache is getting too large
        if len(_transcription_cache) > MAX_CACHE_SIZE:
            _cleanup_old_cache_entries()
            
    except Exception as e:
        logger.warning(f"Cache storage failed: {e}")


def _cleanup_old_cache_entries():
    """Remove old cache entries to prevent memory bloat"""
    current_time = time.time()
    
    # Clean transcription cache
    expired_keys = [
        key for key, timestamp in _cache_timestamps.items()
        if (current_time - timestamp) > CACHE_MAX_AGE and key.startswith("transcription:")
    ]
    
    for key in expired_keys:
        _cache_timestamps.pop(key, None)
        _transcription_cache.pop(key, None)
    
    logger.info(f"Cleaned {len(expired_keys)} expired cache entries")


class FastTranscriptionService:
    """Ultra-fast service class for handling audio transcription"""
    
    def __init__(self):
        logger.info("Initializing FastTranscriptionService")
    
    def transcribe(
        self, 
        request: LocalTranscriptionRequest
    ) -> Union[TranscriptionResponse, LocalTranscriptionError]:
        """
        Ultra-fast transcribe audio file.
        Uses caching for maximum speed.
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting FAST transcription for file: {request.audio_file_path}")
            
            # Prepare request parameters for caching
            request_params = {
                'language': request.language,
                'response_format': request.response_format,
                'temperature': request.temperature,
                'prompt': request.prompt
            }
            
            # Check transcription cache first
            cached_transcription = _get_cached_transcription(request.audio_file_path, request_params)
            
            if cached_transcription:
                transcription_result = cached_transcription
                logger.info("Using cached transcription result")
            else:
                # Transcribe the audio
                transcription_request = TranscriptionRequest(
                    audio_file_path=request.audio_file_path,
                    language=request.language,
                    prompt=request.prompt,
                    response_format=request.response_format,
                    temperature=request.temperature
                )
                
                transcription_result = transcribe_audio_file(transcription_request)
                
                # Check if transcription failed
                if isinstance(transcription_result, TranscriptionError):
                    logger.error(f"Transcription failed: {transcription_result.error_message}")
                    return LocalTranscriptionError(
                        error_type=transcription_result.error_type,
                        error_message=f"Transcription failed: {transcription_result.error_message}",
                        file_path=request.audio_file_path,
                        stage="transcription"
                    )
                
                # Cache successful transcription
                transcription_dict = {
                    'transcript': transcription_result.transcript,
                    'file_path': transcription_result.file_path,
                    'language_detected': transcription_result.language_detected,
                    'duration': transcription_result.duration,
                    'response_format': transcription_result.response_format
                }
                _cache_transcription(request.audio_file_path, request_params, transcription_dict)
                
                logger.info("Transcription completed successfully")
            
            total_time = time.time() - start_time
            logger.info(f"FAST transcription completed in {total_time:.2f}s")
            
            # Create successful response
            if isinstance(transcription_result, dict):
                return TranscriptionResponse(
                    success=True,
                    transcript=transcription_result['transcript'],
                    file_path=transcription_result['file_path'],
                    language_detected=transcription_result.get('language_detected'),
                    duration=transcription_result.get('duration'),
                    response_format=transcription_result['response_format']
                )
            else:
                return TranscriptionResponse(
                    success=True,
                    transcript=transcription_result.transcript,
                    file_path=transcription_result.file_path,
                    language_detected=transcription_result.language_detected,
                    duration=transcription_result.duration,
                    response_format=transcription_result.response_format
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in FAST transcription: {str(e)}")
            return LocalTranscriptionError(
                error_type="UnexpectedError",
                error_message=f"An unexpected error occurred: {str(e)}",
                file_path=request.audio_file_path,
                stage="general"
            )


# Create a global instance of the FAST service
transcription_service = FastTranscriptionService()


def transcribe_audio(
    request: LocalTranscriptionRequest
) -> Union[TranscriptionResponse, LocalTranscriptionError]:
    """
    Ultra-fast convenience function for transcribing audio files.
    """
    return transcription_service.transcribe(request)


def transcribe_simple(audio_file_path: str) -> dict:
    """
    Ultra-fast simple transcription function.
    Uses caching and optimized processing for maximum speed.
    """
    request = LocalTranscriptionRequest(audio_file_path=audio_file_path)
    result = transcription_service.transcribe(request)
    
    if isinstance(result, LocalTranscriptionError):
        raise Exception(f"{result.error_type}: {result.error_message}")
    
    return {
        "transcript": result.transcript,
        "language_detected": result.language_detected,
        "duration": result.duration,
        "file_path": result.file_path
    }


# Utility functions for cache management
def clear_cache():
    """Clear all caches"""
    global _transcription_cache, _cache_timestamps
    _transcription_cache.clear()
    _cache_timestamps.clear()
    logger.info("All caches cleared")


def get_cache_stats() -> dict:
    """Get cache statistics"""
    return {
        "transcription_cache_size": len(_transcription_cache),
        "total_cache_entries": len(_cache_timestamps),
        "cache_enabled": ENABLE_CACHING
    }