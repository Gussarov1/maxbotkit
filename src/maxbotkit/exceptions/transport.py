from maxbotkit.exceptions.base import MaxBotKitError


class TransportError(MaxBotKitError):
    """Raised when the HTTP transport cannot reach the API."""


class RetryableTransportError(TransportError):
    """Raised when the request failed for a retryable transport reason."""
