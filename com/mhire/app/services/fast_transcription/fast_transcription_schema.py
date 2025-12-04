from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from pathlib import Path


class TranscriptionRequest(BaseModel):
    """Schema for transcription request"""
    audio_file_path: str = Field(..., description="Path to the audio file to transcribe")
    language: Optional[str] = Field(None, description="Language code (e.g., 'en', 'es', 'fr')")
    prompt: Optional[str] = Field(None, description="Optional text to guide the model's style")
    response_format: Literal["text", "json", "srt", "verbose_json", "vtt"] = Field(
        default="text", 
        description="Format of the transcript output"
    )
    temperature: float = Field(
        default=0, 
        ge=0, 
        le=1, 
        description="Sampling temperature between 0 and 1. Use 0 for most accurate results."
    )

    @validator('audio_file_path')
    def validate_audio_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError("Audio file path cannot be empty")
        return v.strip()

    @validator('language')
    def validate_language(cls, v):
        if v is not None:
            v = v.strip().lower()
            if len(v) != 2:
                raise ValueError("Language code must be 2 characters (ISO 639-1)")
        return v

    @validator('prompt')
    def validate_prompt(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 224:
                raise ValueError("Prompt must be less than 224 characters")
        return v


class TranscriptionResponse(BaseModel):
    """Schema for transcription response"""
    success: bool = Field(..., description="Whether the transcription was successful")
    transcript: Optional[str] = Field(None, description="The transcribed text")
    file_path: str = Field(..., description="Path of the transcribed file")
    language_detected: Optional[str] = Field(None, description="Detected language of the audio")
    duration: Optional[float] = Field(None, description="Duration of the audio file in seconds")
    response_format: str = Field(..., description="Format of the response")


class TranscriptionError(BaseModel):
    """Schema for transcription error response"""
    success: bool = Field(default=False, description="Always false for error responses")
    error_type: str = Field(..., description="Type of error that occurred")
    error_message: str = Field(..., description="Detailed error message")
    file_path: Optional[str] = Field(None, description="Path of the file that caused the error")
    stage: str = Field(..., description="Stage where error occurred")