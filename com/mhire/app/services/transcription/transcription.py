import os
import logging
import tempfile
from pathlib import Path
from typing import Union, Tuple
import openai
# from com.mhire.app.config.config import OPENAI_API_KEY, WHISPER_MODEL_NAME
from com.mhire.app.services.transcription.transcription_schema import TranscriptionRequest, TranscriptionResponse, TranscriptionError
from com.mhire.app.config.config import Config



config = Config()
OPENAI_API_KEY = config.OPENAI_API_KEY
WHISPER_MODEL_NAME = config.WHISPER_MODEL_NAME

# Try to import pydub for audio preprocessing
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("pydub is available - audio preprocessing enabled")
except ImportError:
    PYDUB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pydub not available - audio preprocessing disabled. Install with: pip install pydub")

logger = logging.getLogger(__name__)

# Validate configuration on module load
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not configured")
    raise ValueError("OPENAI_API_KEY environment variable is required")

if not WHISPER_MODEL_NAME:
    logger.error("WHISPER_MODEL_NAME is not configured")
    raise ValueError("WHISPER_MODEL_NAME configuration is required")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Supported audio formats for OpenAI Whisper
SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB limit for OpenAI API


class TranscriptionService:
    """Service class for handling audio transcription operations with advanced preprocessing"""
    
    def __init__(self):
        self.client = client
        self.model_name = WHISPER_MODEL_NAME
    
    def _preprocess_audio(self, file_path: str) -> Tuple[str, float]:
        """
        Preprocess audio for better speech recognition accuracy.
        Applies normalization, filtering, and format optimization.
        
        Args:
            file_path (str): Path to the original audio file
            
        Returns:
            Tuple[str, float]: (processed_file_path, duration_in_seconds)
        """
        try:
            if not PYDUB_AVAILABLE:
                # Fallback: estimate duration and return original file
                file_size = os.path.getsize(file_path)
                estimated_duration = max(1.0, file_size / 16000.0)  # Rough estimate
                logger.info(f"pydub not available, using original file. Estimated duration: {estimated_duration:.2f}s")
                return file_path, estimated_duration
            
            # Load audio file with pydub
            try:
                audio = AudioSegment.from_file(file_path)
                logger.info("Successfully loaded audio with pydub")
            except Exception as pydub_error:
                logger.warning(f"pydub failed to load audio: {str(pydub_error)}")
                # Fallback: return original file
                file_size = os.path.getsize(file_path)
                estimated_duration = max(1.0, file_size / 16000.0)
                return file_path, estimated_duration
            
            # Get duration in seconds
            duration = len(audio) / 1000.0
            logger.info(f"Original audio duration: {duration:.2f} seconds")
            
            try:
                # Audio preprocessing for better accuracy
                logger.info("Starting audio preprocessing...")
                
                # 1. Normalize volume to optimal level
                audio = audio.normalize()
                logger.debug("Applied volume normalization")
                
                # 2. Apply high-pass filter to reduce low-frequency noise
                audio = audio.high_pass_filter(300)
                logger.debug("Applied high-pass filter (300Hz)")
                
                # 3. Apply low-pass filter to remove very high frequencies
                audio = audio.low_pass_filter(8000)
                logger.debug("Applied low-pass filter (8000Hz)")
                
                # 4. Convert to mono if stereo (reduces file size and improves processing)
                if audio.channels > 1:
                    audio = audio.set_channels(1)
                    logger.debug("Converted to mono")
                
                # 5. Set optimal sample rate for Whisper (16kHz)
                if audio.frame_rate != 16000:
                    audio = audio.set_frame_rate(16000)
                    logger.debug("Set sample rate to 16kHz")
                
                # 6. Export processed audio to temporary file
                processed_path = file_path.replace('.', '_processed.')
                if not processed_path.endswith('.wav'):
                    processed_path = processed_path.rsplit('.', 1)[0] + '_processed.wav'
                
                audio.export(processed_path, format="wav")
                logger.info(f"Audio preprocessing completed. Processed file: {processed_path}")
                
                return processed_path, duration
                
            except Exception as processing_error:
                logger.warning(f"Audio processing failed, using original file: {str(processing_error)}")
                return file_path, duration
                
        except Exception as e:
            logger.error(f"Error in _preprocess_audio: {str(e)}")
            # Final fallback
            try:
                file_size = os.path.getsize(file_path)
                estimated_duration = max(1.0, file_size / 16000.0)
                return file_path, estimated_duration
            except:
                return file_path, 10.0  # Default duration if all else fails
    
    def _calculate_confidence_score(self, transcript_response) -> float:
        """
        Calculate confidence score from Whisper response segments.
        
        Args:
            transcript_response: OpenAI Whisper API response
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        try:
            # Default confidence for Whisper
            default_confidence = 0.85
            
            # Try to extract confidence from segments
            if hasattr(transcript_response, 'segments') and transcript_response.segments:
                total_confidence = 0.0
                segment_count = 0
                
                for segment in transcript_response.segments:
                    if hasattr(segment, 'avg_logprob'):
                        total_confidence += segment.avg_logprob
                        segment_count += 1
                    elif hasattr(segment, '__dict__') and 'avg_logprob' in segment.__dict__:
                        total_confidence += segment.__dict__['avg_logprob']
                        segment_count += 1
                
                if segment_count > 0:
                    avg_confidence = total_confidence / segment_count
                    # Convert log probability to confidence score (0-1)
                    # avg_logprob ranges from -inf to 0, where 0 is highest confidence
                    confidence_score = max(0.0, min(1.0, (avg_confidence + 1.0)))
                    logger.info(f"Calculated confidence score: {confidence_score:.3f}")
                    return confidence_score
            
            logger.info(f"Using default confidence score: {default_confidence}")
            return default_confidence
            
        except Exception as e:
            logger.warning(f"Could not calculate confidence score: {str(e)}")
            return 0.85  # Default confidence
    
    def _validate_audio_file(self, file_path: str) -> None:
        """
        Validate audio file exists, format is supported, and size is within limits.
        
        Args:
            file_path (str): Path to the audio file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format unsupported or file too large
        """
        audio_path = Path(file_path)
        
        # Check if file exists
        if not audio_path.exists():
            logger.error(f"Audio file not found: {file_path}")
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Check file format
        file_extension = audio_path.suffix.lower()
        if file_extension not in SUPPORTED_FORMATS:
            logger.error(f"Unsupported audio format: {file_extension}")
            raise ValueError(f"Unsupported audio format: {file_extension}. Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        
        # Check file size
        file_size = audio_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.error(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)")
            raise ValueError(f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum allowed size (25MB)")
    
    def transcribe_audio(self, request: TranscriptionRequest) -> Union[TranscriptionResponse, TranscriptionError]:
        """
        Transcribe audio file using OpenAI Whisper API with advanced accuracy optimizations.
        Includes audio preprocessing, confidence scoring, and enhanced error handling.
        
        Args:
            request (TranscriptionRequest): Transcription request with parameters
            
        Returns:
            Union[TranscriptionResponse, TranscriptionError]: Response or error object
        """
        processed_file_path = None
        
        try:
            # Validate the audio file
            self._validate_audio_file(request.audio_file_path)
            
            logger.info(f"Starting advanced transcription for file: {request.audio_file_path}")
            logger.info(f"Using model: {self.model_name}")
            logger.info(f"Response format: {request.response_format}")
            
            # Step 1: Preprocess audio for better accuracy
            processed_file_path, duration = self._preprocess_audio(request.audio_file_path)
            logger.info(f"Audio preprocessing completed. Duration: {duration:.2f}s")
            
            # Step 2: Prepare transcription parameters with accuracy optimizations
            # Use verbose_json for confidence scoring when possible
            use_verbose = request.response_format in ["json", "verbose_json"] or request.response_format == "text"
            actual_format = "verbose_json" if use_verbose else request.response_format
            
            transcription_params = {
                "model": self.model_name,
                "response_format": actual_format,
                "temperature": request.temperature
            }
            
            # Add optional parameters if provided
            if request.language:
                transcription_params["language"] = request.language
                logger.info(f"Using specified language: {request.language}")
            
            # Enhanced prompt handling for better accuracy
            if request.prompt:
                # Clean and optimize the prompt
                cleaned_prompt = request.prompt.strip()
                if len(cleaned_prompt) > 0:
                    transcription_params["prompt"] = cleaned_prompt
                    logger.info(f"Using prompt for context: {cleaned_prompt[:50]}...")
            
            # Add context-aware prompts for dating app content if no custom prompt
            elif not request.prompt:
                # Default prompts that help with dating app context
                dating_context_prompts = [
                    "This is a conversation from a dating app. Include proper punctuation and capitalization.",
                    "Dating app voice message with casual conversation.",
                    "Personal conversation between two people getting to know each other."
                ]
                transcription_params["prompt"] = dating_context_prompts[0]
                logger.info("Using default dating context prompt for better accuracy")
            
            # Step 3: Perform transcription with retry logic for better reliability
            max_retries = 2
            transcript = None
            
            for attempt in range(max_retries + 1):
                try:
                    with open(processed_file_path, "rb") as audio_file:
                        transcript = self.client.audio.transcriptions.create(
                            file=audio_file,
                            **transcription_params
                        )
                    break  # Success, exit retry loop
                    
                except openai.RateLimitError as e:
                    if attempt < max_retries:
                        import time
                        wait_time = (attempt + 1) * 2  # Exponential backoff
                        logger.warning(f"Rate limit hit, retrying in {wait_time} seconds... (attempt {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise e
                        
                except openai.APITimeoutError as e:
                    if attempt < max_retries:
                        logger.warning(f"API timeout, retrying... (attempt {attempt + 1})")
                        continue
                    else:
                        raise e
            
            logger.info(f"Transcription completed successfully for: {request.audio_file_path}")
            logger.info(f"Transcript type: {type(transcript)}")
            
            # Step 4: Extract results and calculate confidence
            transcript_text = None
            detected_language = None
            confidence_score = 0.85  # Default
            
            if actual_format == "verbose_json":
                # Extract from verbose JSON response
                if hasattr(transcript, 'text'):
                    transcript_text = transcript.text
                    detected_language = getattr(transcript, 'language', None)
                    confidence_score = self._calculate_confidence_score(transcript)
                else:
                    transcript_text = str(transcript)
                    
                # Convert back to requested format if needed
                if request.response_format == "text":
                    # Keep the text but log the confidence
                    logger.info(f"Transcription confidence: {confidence_score:.3f}")
                    
            elif request.response_format == "text":
                # For text format, OpenAI returns a plain string
                if isinstance(transcript, str):
                    transcript_text = transcript
                else:
                    transcript_text = getattr(transcript, 'text', str(transcript))
                    
            elif request.response_format in ["json", "verbose_json"]:
                # For JSON formats
                if hasattr(transcript, 'text'):
                    transcript_text = transcript.text
                    detected_language = getattr(transcript, 'language', None)
                    confidence_score = self._calculate_confidence_score(transcript)
                else:
                    transcript_text = str(transcript)
                    
            elif request.response_format in ["srt", "vtt"]:
                # For subtitle formats, return the raw response as string
                transcript_text = str(transcript)
                
            else:
                # Fallback for any other format
                if hasattr(transcript, 'text'):
                    transcript_text = transcript.text
                else:
                    transcript_text = str(transcript)
            
            # Step 5: Log accuracy metrics
            if transcript_text:
                word_count = len(transcript_text.split())
                logger.info(f"Transcription metrics - Words: {word_count}, Duration: {duration:.2f}s, "
                           f"Confidence: {confidence_score:.3f}, Language: {detected_language or 'auto'}")
            
            return TranscriptionResponse(
                success=True,
                transcript=transcript_text,
                file_path=request.audio_file_path,
                language_detected=detected_language,
                duration=duration,
                response_format=request.response_format
            )
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {str(e)}")
            return TranscriptionError(
                error_type="FileNotFoundError",
                error_message=str(e),
                file_path=request.audio_file_path
            )
        
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return TranscriptionError(
                error_type="ValidationError",
                error_message=str(e),
                file_path=request.audio_file_path
            )
        
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error during transcription: {str(e)}")
            return TranscriptionError(
                error_type="OpenAIError",
                error_message=f"API error: {str(e)}",
                file_path=request.audio_file_path
            )
        
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            logger.error(f"Transcript object type: {type(transcript) if 'transcript' in locals() else 'Not available'}")
            return TranscriptionError(
                error_type="UnexpectedError",
                error_message=f"An unexpected error occurred: {str(e)}",
                file_path=request.audio_file_path
            )
        
        finally:
            # Cleanup processed audio file if it's different from original
            if (processed_file_path and 
                processed_file_path != request.audio_file_path and 
                os.path.exists(processed_file_path)):
                try:
                    os.unlink(processed_file_path)
                    logger.debug(f"Cleaned up processed file: {processed_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup processed file {processed_file_path}: {str(cleanup_error)}")


# Create a global instance of the service
transcription_service = TranscriptionService()


def transcribe_audio_file(request: TranscriptionRequest) -> Union[TranscriptionResponse, TranscriptionError]:
    """
    Convenience function for transcribing audio files.
    
    Args:
        request (TranscriptionRequest): Transcription request
        
    Returns:
        Union[TranscriptionResponse, TranscriptionError]: Response or error object
    """
    return transcription_service.transcribe_audio(request)


def transcribe_simple(audio_file_path: str) -> str:
    """
    Simple transcription function for backward compatibility.
    Returns only the transcript text or raises an exception.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    request = TranscriptionRequest(audio_file_path=audio_file_path)
    result = transcription_service.transcribe_audio(request)
    
    if isinstance(result, TranscriptionError):
        raise Exception(f"{result.error_type}: {result.error_message}")
    
    return result.transcript