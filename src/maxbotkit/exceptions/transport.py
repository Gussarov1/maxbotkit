from maxbotkit.exceptions.base import MaxBotKitError


class TransportError(MaxBotKitError):
    """Raised when the HTTP transport cannot reach the API."""
