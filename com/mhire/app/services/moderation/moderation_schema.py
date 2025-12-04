from pydantic import BaseModel
from typing import Dict, Optional

class ModerationRequest(BaseModel):
    text: str

class CustomFlags(BaseModel):
    # explicit_content: bool = False
    # suggestive_context: bool = False
    # body_shaming: bool = False
    # emotional_abuse: bool = False
    # racism_hate_speech: bool = False
    # transactional_dating: bool = False
    # sexism_misogyny_transphobia: bool = False
    pass

class ModerationResponse(BaseModel):
    text: str
    flagged: bool
    # detection_method: str
    # openai_flagged: bool
    # custom_flagged: bool
    # custom_flags: CustomFlags
    # reason: str
    # api_call_made: bool
    # categories: Dict = {}
    # category_scores: Dict = {}