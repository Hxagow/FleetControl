import re
from django.core.exceptions import ValidationError


# couvre les plages d'emojis courantes
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF"
    "]",
    flags=re.UNICODE,
)


def no_emoji_validator(value):
    """Autorise tout caractère sauf les emojis."""
    if value is None:
        return

    try:
        s = str(value)
    except Exception:
        return

    if _EMOJI_RE.search(s):
        raise ValidationError("Emojis non autorisés.")
