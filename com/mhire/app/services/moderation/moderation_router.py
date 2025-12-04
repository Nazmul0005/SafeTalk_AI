from fastapi import APIRouter, HTTPException
from com.mhire.app.services.moderation.moderation_schema import ModerationRequest, ModerationResponse
from com.mhire.app.services.moderation.moderation import moderate_text
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/moderation", tags=["moderation"])

@router.post("/moderate-text", response_model=ModerationResponse)
async def moderate_text_endpoint(request: ModerationRequest):
    """
    Endpoint to moderate text content using hybrid approach:
    1. Fast custom pattern detection
    2. OpenAI context analysis for borderline cases
    """
    try:
        logger.info(f"Received moderation request for text: {request.text[:50]}...")
        
        # Call the moderation function
        result = moderate_text(request.text)
        
        # Create response
        response = ModerationResponse(
            text=result["text"],
            flagged=result["flagged"]
        )
        
        logger.info(f"Moderation completed. Flagged: {result['flagged']}")
        return response
        
    except Exception as e:
        logger.error(f"Error in moderation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Moderation failed: {str(e)}")