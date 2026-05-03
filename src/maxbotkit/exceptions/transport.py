from maxbotkit.exceptions.base import MaxBotError


class TransportError(MaxBotError):
    """Raised when the HTTP transport cannot reach the API."""
