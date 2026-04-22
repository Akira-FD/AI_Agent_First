class AIAppError(Exception):
    """Base application exception."""


class ToolValidationError(AIAppError):
    """Raised when tool input is invalid."""
