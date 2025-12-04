from com.mhire.app.utils.pattern_utils import (
    EXPLICIT_PATTERNS,
    SUGGESTIVE_CONTEXT_PATTERNS,
    HARASSMENT_PATTERNS,
    BODY_SHAMING_PATTERNS,
    EMOTIONAL_ABUSE_PATTERNS,
    RACISM_HATE_SPEECH_PATTERNS,
    TRANSACTIONAL_DATING_PATTERNS,
    SEXISM_MISOGYNY_TRANSPHOBIA_PATTERNS,
)



"""
Moderation configuration for dating app
Adjust these settings based on your app's content policy requirements
"""

# Custom thresholds for different content categories
# Lower values = stricter moderation
MODERATION_THRESHOLDS = {
    "sexual": 0.1,          # 10% - Flag sexual content above this threshold
    "harassment": 0.05,     # 5% - Flag harassment content above this threshold  
    "hate": 0.05,          # 5% - Flag hate speech above this threshold
    "violence": 0.1,       # 10% - Flag violent content above this threshold
    "sexual_minors": 0.01, # 1% - Very strict for minor-related content
    "sexual/minors": 0.01, # 1% - Alternative key format for minors
}

# Explicit words and phrases that should be flagged regardless of OpenAI scores
EXPLICIT_PATTERNS = EXPLICIT_PATTERNS

# Context patterns that indicate suggestive content
SUGGESTIVE_CONTEXT_PATTERNS = SUGGESTIVE_CONTEXT_PATTERNS

# Harassment patterns specific to dating contexts
HARASSMENT_PATTERNS = HARASSMENT_PATTERNS

# Body shaming and appearance-based harassment patterns
BODY_SHAMING_PATTERNS = BODY_SHAMING_PATTERNS
# Emotional abuse and manipulation patterns
EMOTIONAL_ABUSE_PATTERNS = EMOTIONAL_ABUSE_PATTERNS

# Racism and hate speech patterns
RACISM_HATE_SPEECH_PATTERNS = RACISM_HATE_SPEECH_PATTERNS

# Transactional and sugar-dating language patterns
TRANSACTIONAL_DATING_PATTERNS = TRANSACTIONAL_DATING_PATTERNS

# Sexism, misogyny, and transphobia patterns
SEXISM_MISOGYNY_TRANSPHOBIA_PATTERNS = SEXISM_MISOGYNY_TRANSPHOBIA_PATTERNS

# Configuration for different moderation levels
MODERATION_LEVELS = {
    "strict": {
        "sexual": 0.05,
        "harassment": 0.03,
        "hate": 0.03,
        "violence": 0.05,
    },
    "moderate": {
        "sexual": 0.1,
        "harassment": 0.05,
        "hate": 0.05,
        "violence": 0.1,
    },
    "lenient": {
        "sexual": 0.2,
        "harassment": 0.1,
        "hate": 0.1,
        "violence": 0.15,
    }
}

# Default moderation level
DEFAULT_MODERATION_LEVEL = "moderate"

def get_thresholds(level: str = None) -> dict:
    """Get moderation thresholds for specified level"""
    if level is None:
        level = DEFAULT_MODERATION_LEVEL
    
    return MODERATION_LEVELS.get(level, MODERATION_LEVELS[DEFAULT_MODERATION_LEVEL])