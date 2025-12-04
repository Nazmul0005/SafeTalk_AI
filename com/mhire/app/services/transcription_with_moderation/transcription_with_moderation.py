import logging
import asyncio
import concurrent.futures
import hashlib
import time
from typing import Union, Optional, Tuple
from functools import lru_cache
from pathlib import Path

from com.mhire.app.services.transcription.transcription import transcribe_audio_file
from com.mhire.app.services.transcription.transcription_schema import TranscriptionRequest, TranscriptionError
from com.mhire.app.services.moderation.moderation import moderate_text, check_custom_patterns_only
from com.mhire.app.services.transcription_with_moderation.transcription_with_moderation_schema import (
    TranscriptionWithModerationRequest,
    TranscriptionWithModerationResponse,
    TranscriptionWithModerationError
)

logger = logging.getLogger(__name__)

# Performance optimizations
ENABLE_CACHING = True
ENABLE_FAST_MODERATION = True  # Use custom patterns first, skip OpenAI if flagged
CACHE_MAX_AGE = 3600  # 1 hour cache TTL
MAX_CACHE_SIZE = 1000

# Global caches
_transcription_cache = {}
_moderation_cache = {}
_cache_timestamps = {}

# Thread pool for concurrent operations
_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)


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


def _get_cached_moderation(text: str) -> Optional[dict]:
    """Get cached moderation result if available"""
    if not ENABLE_CACHING:
        return None
    
    try:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"moderation:{text_hash}"
        
        if _is_cache_valid(cache_key) and cache_key in _moderation_cache:
            logger.info("Cache hit for moderation")
            return _moderation_cache[cache_key]
    except Exception as e:
        logger.warning(f"Moderation cache lookup failed: {e}")
    
    return None


def _cache_moderation(text: str, result: dict):
    """Cache moderation result"""
    if not ENABLE_CACHING:
        return
    
    try:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"moderation:{text_hash}"
        
        _moderation_cache[cache_key] = result
        _cache_timestamps[cache_key] = time.time()
        
        # Clean old cache entries if cache is getting too large
        if len(_moderation_cache) > MAX_CACHE_SIZE:
            _cleanup_old_cache_entries()
            
    except Exception as e:
        logger.warning(f"Moderation cache storage failed: {e}")


def _cleanup_old_cache_entries():
    """Remove old cache entries to prevent memory bloat"""
    current_time = time.time()
    
    # Clean transcription cache
    expired_keys = [
        key for key, timestamp in _cache_timestamps.items()
        if (current_time - timestamp) > CACHE_MAX_AGE
    ]
    
    for key in expired_keys:
        _cache_timestamps.pop(key, None)
        if key.startswith("transcription:"):
            _transcription_cache.pop(key, None)
        elif key.startswith("moderation:"):
            _moderation_cache.pop(key, None)
    
    logger.info(f"Cleaned {len(expired_keys)} expired cache entries")


def _fast_moderate_text(text: str) -> dict:
    """Ultra-fast moderation using custom patterns first"""
    if not text or not text.strip():
        return {
            "text": text,
            "flagged": False,
            "reason": "Empty text",
            "custom_flagged": False,
            "custom_flags": {}
        }
    
    # Check cache first
    cached_result = _get_cached_moderation(text)
    if cached_result:
        return cached_result
    
    if ENABLE_FAST_MODERATION:
        # Step 1: Lightning-fast custom pattern check
        custom_flagged, custom_flags, custom_reason = check_custom_patterns_only(text)
        
        if custom_flagged:
            # If custom patterns flag it, no need for OpenAI API call
            result = {
                "text": text,
                "flagged": True,
                "reason": custom_reason,
                "custom_flagged": True,
                "custom_flags": custom_flags
            }
            _cache_moderation(text, result)
            return result
    
    # Step 2: Full moderation only if custom patterns didn't flag it
    result = moderate_text(text)
    _cache_moderation(text, result)
    return result


class FastTranscriptionWithModerationService:
    """Ultra-fast service class for handling audio transcription with content moderation"""
    
    def __init__(self):
        logger.info("Initializing FastTranscriptionWithModerationService")
        self._executor = _thread_pool
    
    def transcribe_and_moderate(
        self, 
        request: TranscriptionWithModerationRequest
    ) -> Union[TranscriptionWithModerationResponse, TranscriptionWithModerationError]:
        """
        Ultra-fast transcribe audio file and moderate the resulting text.
        Uses caching and optimized moderation for maximum speed.
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting FAST transcription with moderation for file: {request.audio_file_path}")
            
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
                # Step 1: Transcribe the audio
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
                    return TranscriptionWithModerationError(
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
            
            # Extract transcript text
            transcript_text = transcription_result.get('transcript') if isinstance(transcription_result, dict) else transcription_result.transcript
            
            # Step 2: Ultra-fast moderation
            moderation_start = time.time()
            moderation_result = _fast_moderate_text(transcript_text)
            moderation_time = time.time() - moderation_start
            
            # Extract moderation information
            is_flagged = moderation_result.get("flagged", False)
            moderation_reason = moderation_result.get("reason", "No issues detected")
            
            total_time = time.time() - start_time
            logger.info(f"FAST processing completed in {total_time:.2f}s (moderation: {moderation_time:.3f}s). Flagged: {is_flagged}")
            
            # Create successful response
            if isinstance(transcription_result, dict):
                return TranscriptionWithModerationResponse(
                    success=True,
                    transcript=transcription_result['transcript'],
                    file_path=transcription_result['file_path'],
                    language_detected=transcription_result.get('language_detected'),
                    duration=transcription_result.get('duration'),
                    response_format=transcription_result['response_format'],
                    moderation_flagged=is_flagged,
                    moderation_reason=moderation_reason,
                    is_safe=not is_flagged
                )
            else:
                return TranscriptionWithModerationResponse(
                    success=True,
                    transcript=transcription_result.transcript,
                    file_path=transcription_result.file_path,
                    language_detected=transcription_result.language_detected,
                    duration=transcription_result.duration,
                    response_format=transcription_result.response_format,
                    moderation_flagged=is_flagged,
                    moderation_reason=moderation_reason,
                    is_safe=not is_flagged
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in FAST transcription with moderation: {str(e)}")
            return TranscriptionWithModerationError(
                error_type="UnexpectedError",
                error_message=f"An unexpected error occurred: {str(e)}",
                file_path=request.audio_file_path,
                stage="general"
            )


# Create a global instance of the FAST service
transcription_with_moderation_service = FastTranscriptionWithModerationService()


def transcribe_and_moderate_audio(
    request: TranscriptionWithModerationRequest
) -> Union[TranscriptionWithModerationResponse, TranscriptionWithModerationError]:
    """
    Ultra-fast convenience function for transcribing and moderating audio files.
    """
    return transcription_with_moderation_service.transcribe_and_moderate(request)


def transcribe_and_moderate_simple(audio_file_path: str) -> dict:
    """
    Ultra-fast simple transcription with moderation function.
    Uses caching and optimized processing for maximum speed.
    """
    request = TranscriptionWithModerationRequest(audio_file_path=audio_file_path)
    result = transcription_with_moderation_service.transcribe_and_moderate(request)
    
    if isinstance(result, TranscriptionWithModerationError):
        raise Exception(f"{result.error_type}: {result.error_message}")
    
    return {
        "transcript": result.transcript,
        "is_safe": result.is_safe,
        "moderation_flagged": result.moderation_flagged,
        "moderation_reason": result.moderation_reason,
        "language_detected": result.language_detected
    }


# Utility functions for cache management
def clear_cache():
    """Clear all caches"""
    global _transcription_cache, _moderation_cache, _cache_timestamps
    _transcription_cache.clear()
    _moderation_cache.clear()
    _cache_timestamps.clear()
    logger.info("All caches cleared")


def get_cache_stats() -> dict:
    """Get cache statistics"""
    return {
        "transcription_cache_size": len(_transcription_cache),
        "moderation_cache_size": len(_moderation_cache),
        "total_cache_entries": len(_cache_timestamps),
        "cache_enabled": ENABLE_CACHING,
        "fast_moderation_enabled": ENABLE_FAST_MODERATION
    }