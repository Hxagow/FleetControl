import string
from django.core.exceptions import ValidationError


def ascii_only_validator(value):
    """Allows only printable ASCII characters."""
    if value is None:
        return

    try:
        s = str(value)
    except Exception:
        return

    for c in s:
        if c not in string.printable:
            raise ValidationError("Caractères spéciaux non autorisés.")
