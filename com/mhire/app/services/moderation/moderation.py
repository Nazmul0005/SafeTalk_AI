# from com.mhire.app.client.client import clientModereration
import re
from typing import Dict, Tuple
import logging
import openai
from com.mhire.app.utils.moderation_utils import (
    EXPLICIT_PATTERNS,
    SUGGESTIVE_CONTEXT_PATTERNS,
    HARASSMENT_PATTERNS,
    BODY_SHAMING_PATTERNS,
    EMOTIONAL_ABUSE_PATTERNS,
    RACISM_HATE_SPEECH_PATTERNS,
    TRANSACTIONAL_DATING_PATTERNS,
    SEXISM_MISOGYNY_TRANSPHOBIA_PATTERNS,
)

from com.mhire.app.config.config import Config
config = Config()
OPENAI_API_KEY = config.OPENAI_API_KEY
clientModereration = openai.OpenAI(api_key = OPENAI_API_KEY)


# Configure logging
logger = logging.getLogger(__name__)

# Custom thresholds for dating app (stricter than OpenAI defaults)
CUSTOM_THRESHOLDS = {
    "sexual": 0.05,  # Lowered from 0.1 to catch subtle sexual content
    "harassment": 0.05,  # Flag if harassment score > 5%
    "hate": 0.05,  # Flag if hate score > 5%
    "violence": 0.1,  # Flag if violence score > 10%
    "sexual_minors": 0.01,  # Very strict for minors content
    "sexual/minors": 0.01,  # Alternative key format
}

# Explicit inappropriate words/phrases for dating context
INAPPROPRIATE_PATTERNS = [
    r'\b(fuck|fucking|fucked)\b',
    r'\b(pussy|dick|cock|penis|vagina)\b',
    r'\b(cum|cumming|orgasm)\b',
    r'\b(horny|wet|hard|erect)\b',
    r'\b(suck|lick|taste|swallow)\b.*\b(you|me|it)\b',
    r'\b(naked|nude|undress|strip)\b',
    r'\b(bedroom|bed|shower|bath)\b.*\b(together|with me|with you)\b',
    r'\b(kiss|touch|feel|grab)\b.*\b(body|skin|lips|neck)\b',
    r'\bhow far.*\b(down|up|deep)\b',
    r'\bslowly.*\b(kiss|touch|lick)\b',
    r'\bmake.*\b(love|out|you moan)\b',
    r'\b(desire|want|need).*\b(you|your body)\b',
    r'\b(turn.*on|turned on|aroused)\b',
    r'\b(dirty|naughty|bad).*\b(things|thoughts|ideas)\b',
    r'\b(69)\b',
    
    # Subtle sexual implications
    r'\bwithout\s+(them|clothes|clothing)\b',
    r'\bcan\'t\s+imagine\s+how\s+(good|sexy|hot)\s+you\b',
    r'\bhow\s+(good|sexy|hot)\s+you\'ll\s+look\s+without\b',
    r'\blook\s+(good|sexy|hot)\s+without\b',
    r'\bwhat\s+you\'re\s+wearing\s+under\b',
    r'\bunderneath\s+(those|your)\s+(clothes|clothing)\b'
]

def check_custom_patterns_only(text: str) -> Tuple[bool, dict, str]:
    """
    Fast custom pattern detection without OpenAI API call
    Returns: (is_flagged, custom_flags_dict, reason)
    """
    custom_flags = {}
    reasons = []
    text_lower = text.lower()
    
    # Check for explicit inappropriate patterns
    explicit_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                          for pattern in INAPPROPRIATE_PATTERNS)
    
    if explicit_matches:
        custom_flags["explicit_content"] = True
        reasons.append("Explicit sexual/inappropriate language detected")
    else:
        custom_flags["explicit_content"] = False
    
    # Check for suggestive context patterns
    suggestive_indicators = [
        r'\btonight.*\bwant\b',
        r'\bquestion.*\bhow far\b',
        r'\bslowly.*\bkiss.*\bdown\b',
        r'\bfrom.*\blips.*\bdown\b',
    ]
    
    suggestive_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                           for pattern in suggestive_indicators)
    
    if suggestive_matches:
        custom_flags["suggestive_context"] = True
        reasons.append("Suggestive/sexual context detected")
    else:
        custom_flags["suggestive_context"] = False
    
    # Check for body shaming and appearance-based harassment
    body_shaming_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                              for pattern in BODY_SHAMING_PATTERNS)
    
    if body_shaming_matches:
        custom_flags["body_shaming"] = True
        reasons.append("Body shaming/appearance-based harassment detected")
    else:
        custom_flags["body_shaming"] = False
    
    # Check for emotional abuse and manipulation
    emotional_abuse_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                                 for pattern in EMOTIONAL_ABUSE_PATTERNS)
    
    if emotional_abuse_matches:
        custom_flags["emotional_abuse"] = True
        reasons.append("Emotional abuse/manipulation detected")
    else:
        custom_flags["emotional_abuse"] = False
    
    # Check for racism and hate speech
    racism_hate_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                             for pattern in RACISM_HATE_SPEECH_PATTERNS)
    
    if racism_hate_matches:
        custom_flags["racism_hate_speech"] = True
        reasons.append("Racism/hate speech detected")
    else:
        custom_flags["racism_hate_speech"] = False
    
    # Check for transactional and sugar-dating language
    transactional_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                               for pattern in TRANSACTIONAL_DATING_PATTERNS)
    
    if transactional_matches:
        custom_flags["transactional_dating"] = True
        reasons.append("Transactional/sugar-dating language detected")
    else:
        custom_flags["transactional_dating"] = False
    
    # Check for sexism, misogyny, and transphobia
    sexism_matches = any(re.search(pattern, text_lower, re.IGNORECASE) 
                        for pattern in SEXISM_MISOGYNY_TRANSPHOBIA_PATTERNS)
    
    if sexism_matches:
        custom_flags["sexism_misogyny_transphobia"] = True
        reasons.append("Sexism/misogyny/transphobia detected")
    else:
        custom_flags["sexism_misogyny_transphobia"] = False
    
    # Overall flagging decision for custom patterns
    is_flagged = any([
        custom_flags.get("explicit_content", False),
        custom_flags.get("suggestive_context", False),
        custom_flags.get("body_shaming", False),
        custom_flags.get("emotional_abuse", False),
        custom_flags.get("racism_hate_speech", False),
        custom_flags.get("transactional_dating", False),
        custom_flags.get("sexism_misogyny_transphobia", False)
    ])
    
    reason = "; ".join(reasons) if reasons else "No custom pattern violations detected"
    
    return is_flagged, custom_flags, reason

def openai_context_analysis(text: str) -> Tuple[bool, dict, str]:
    """
    OpenAI context analysis for subtle/borderline cases
    Returns: (is_flagged, openai_result_dict, reason)
    """
    try:
        logger.info("Running OpenAI context analysis for borderline content")
        
        # Get OpenAI moderation response
        response = clientModereration.moderations.create(input=text)
        openai_result = response.results[0]
        
        # Check against custom thresholds
        flagged_categories = []
        for category, threshold in CUSTOM_THRESHOLDS.items():
            score = openai_result.category_scores.model_dump().get(category, 0)
            if score > threshold:
                flagged_categories.append(f"{category} ({score:.2%})")
        
        is_flagged = openai_result.flagged or len(flagged_categories) > 0
        
        reason = "OpenAI detected harmful context/intent"
        if flagged_categories:
            reason += f": {', '.join(flagged_categories)}"
        
        openai_data = {
            "categories": openai_result.categories.model_dump(),
            "category_scores": openai_result.category_scores.model_dump(),
            "openai_flagged": openai_result.flagged,
            "custom_threshold_violations": flagged_categories
        }
        
        return is_flagged, openai_data, reason
        
    except Exception as e:
        logger.error(f"OpenAI context analysis failed: {str(e)}")
        # Fallback: don't flag if API fails
        return False, {}, f"Context analysis failed: {str(e)}"

def moderate_text(transcribed_text: str) -> dict:
    """
    Optimized hybrid moderation: Custom patterns first, then OpenAI context analysis if needed
    """
    logger.info(f"Starting moderation for text: {transcribed_text[:50]}...")
    
    # Step 1: Quick custom pattern check
    custom_flagged, custom_flags, custom_reason = check_custom_patterns_only(transcribed_text)
    
    if custom_flagged:
        logger.info("Content flagged by custom patterns - no API call needed")
        return {
            "text": transcribed_text,
            "flagged": True,
            "custom_flags": custom_flags,
        }
    
    # Step 2: OpenAI context analysis for borderline cases
    logger.info("Custom patterns clean - running OpenAI context analysis")
    openai_flagged, openai_data, openai_reason = openai_context_analysis(transcribed_text)
    
    final_result = {
        "text": transcribed_text,
        "flagged": openai_flagged,
        "detection_method": "openai_context_analysis" if openai_flagged else "clean",
        "openai_flagged": openai_data.get("openai_flagged", False),
        "custom_flagged": False,
        "custom_flags": custom_flags,
        "reason": openai_reason if openai_flagged else "Content appears safe after full analysis",
        "api_call_made": True,
        "categories": openai_data.get("categories", {}),
        "category_scores": openai_data.get("category_scores", {})
    }
    
    if openai_flagged:
        logger.info("Content flagged by OpenAI context analysis")
    else:
        logger.info("Content passed all moderation checks")
    
    return final_result

# Legacy function for backward compatibility
def check_custom_moderation(text: str, openai_scores: dict) -> Tuple[bool, dict, str]:
    """
    Legacy function - kept for backward compatibility
    """
    return check_custom_patterns_only(text)