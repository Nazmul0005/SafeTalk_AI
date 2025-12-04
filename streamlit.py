import streamlit as st
import os
import tempfile
from pathlib import Path
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import project services
try:
    from com.mhire.app.services.moderation.moderation import moderate_text
    from com.mhire.app.services.transcription.transcription import transcribe_audio_file
    from com.mhire.app.services.transcription.transcription_schema import TranscriptionRequest, TranscriptionError
    from com.mhire.app.services.transcription_with_moderation.transcription_with_moderation import transcribe_and_moderate_audio
    from com.mhire.app.services.transcription_with_moderation.transcription_with_moderation_schema import (
        TranscriptionWithModerationRequest,
        TranscriptionWithModerationError
    )
except ImportError as e:
    st.error(f"Failed to import project modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="MHire Content Moderation & Transcription",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ MHire Content Moderation & Transcription")

# Sidebar navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose a Service", [
    "Text Moderation", 
    "Audio Transcription",
    "Ultra-Fast Transcription + Moderation"
])

if app_mode == "Text Moderation":
    st.header("📝 Text Moderation")
    st.write("Analyze text for inappropriate content using hybrid moderation (Custom Patterns + OpenAI).")

    text_input = st.text_area("Enter text to moderate:", height=150)
    
    if st.button("Moderate Text"):
        if text_input.strip():
            with st.spinner("Moderating..."):
                try:
                    result = moderate_text(text_input)
                    
                    # Display Result
                    st.subheader("Moderation Result")
                    
                    if result.get("flagged"):
                        st.error(f"⚠️ Content Flagged: {result.get('reason', 'Unknown reason')}")
                    else:
                        st.success("✅ Content appears safe.")
                    
                    # Detailed JSON output
                    with st.expander("View Detailed Analysis"):
                        st.json(result)
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to moderate.")

elif app_mode == "Audio Transcription":
    st.header("🎙️ Audio Transcription")
    st.write("Transcribe audio files using OpenAI Whisper with advanced preprocessing.")

    uploaded_file = st.file_uploader("Upload an audio file", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        if st.button("Transcribe Audio"):
            with st.spinner("Transcribing..."):
                temp_file_path = None
                try:
                    # Save uploaded file to temp file
                    suffix = Path(uploaded_file.name).suffix
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_file_path = temp_file.name
                    
                    # Create request
                    request = TranscriptionRequest(
                        audio_file_path=temp_file_path,
                        response_format="text",
                        temperature=0,
                        prompt="This is a conversation from a dating app. Include proper punctuation and capitalization."
                    )
                    
                    # Transcribe
                    result = transcribe_audio_file(request)
                    
                    if isinstance(result, TranscriptionError):
                        st.error(f"Transcription Failed: {result.error_message}")
                    else:
                        st.success("Transcription Complete!")
                        st.subheader("Transcript:")
                        st.write(result.transcript)
                        
                        st.info(f"Duration: {result.duration:.2f} seconds")
                        
                        if result.language_detected:
                            st.caption(f"Detected Language: {result.language_detected}")

                except Exception as e:
                    st.error(f"An error occurred during transcription: {str(e)}")
                
                finally:
                    # Cleanup temp file
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.unlink(temp_file_path)
                        except Exception as e:
                            logger.warning(f"Failed to delete temp file: {e}")

elif app_mode == "Ultra-Fast Transcription + Moderation":
    st.header("⚡ Ultra-Fast Transcription with Moderation")
    st.write("Drag and drop an audio file for ultra-fast transcription and content moderation in one step.")
    st.info("🚀 This feature uses caching and optimized processing for maximum speed!")

    uploaded_file = st.file_uploader(
        "Drag and drop your audio file here", 
        type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'],
        key="ultra_fast_uploader"
    )
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        if st.button("🚀 Process Audio (Transcribe + Moderate)", type="primary"):
            start_time = time.time()
            with st.spinner("Processing... (Transcribing and moderating)"):
                temp_file_path = None
                try:
                    # Save uploaded file to temp file
                    suffix = Path(uploaded_file.name).suffix
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_file_path = temp_file.name
                    
                    # Create ultra-fast request
                    request = TranscriptionWithModerationRequest(
                        audio_file_path=temp_file_path,
                        response_format="text",
                        temperature=0
                    )
                    
                    # Process with ultra-fast transcription and moderation
                    result = transcribe_and_moderate_audio(request)
                    
                    processing_time = time.time() - start_time
                    
                    if isinstance(result, TranscriptionWithModerationError):
                        st.error(f"❌ Processing Failed: {result.error_message}")
                        st.caption(f"Error at stage: {result.stage}")
                    else:
                        # Display processing time
                        st.success(f"✅ Processing Complete in {processing_time:.3f} seconds!")
                        
                        # Create two columns for results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("📄 Transcript:")
                            st.write(result.transcript)
                        
                        with col2:
                            st.subheader("🛡️ Moderation Status:")
                            
                            if result.is_safe:
                                st.success("✅ Content is Safe")
                            else:
                                st.error("⚠️ Content Flagged")
                            
                            if result.moderation_flagged:
                                st.warning(f"**Reason:** {result.moderation_reason}")
                            
                            # Additional info
                            st.divider()
                            st.metric("Duration", f"{result.duration:.2f}s")
                            
                            if result.language_detected:
                                st.metric("Language", result.language_detected.upper())
                        
                        # Detailed results in expander
                        with st.expander("📊 View Detailed Results"):
                            st.json({
                                "transcript": result.transcript,
                                "is_safe": result.is_safe,
                                "moderation_flagged": result.moderation_flagged,
                                "moderation_reason": result.moderation_reason,
                                "duration": result.duration,
                                "language_detected": result.language_detected,
                                "processing_time": round(processing_time, 3)
                            })

                except Exception as e:
                    st.error(f"❌ An error occurred during processing: {str(e)}")
                    logger.error(f"Ultra-fast processing error: {str(e)}", exc_info=True)
                
                finally:
                    # Cleanup temp file
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.unlink(temp_file_path)
                        except Exception as e:
                            logger.warning(f"Failed to delete temp file: {e}")

st.sidebar.markdown("---")
st.sidebar.info("MHire AI Services v1.0")
