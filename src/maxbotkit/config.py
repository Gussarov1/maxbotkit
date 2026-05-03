from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(slots=True)
class RetryConfig:
    """Controls retry behavior for retry-safe client requests.

    Attributes:
        attempts: Total number of attempts including the initial request.
        backoff_base: Initial backoff delay in seconds.
        backoff_max: Maximum backoff delay in seconds.
        jitter: Whether to randomize each backoff interval slightly.
        jitter_ratio: Maximum percentage of the delay used for jitter.
    """

    attempts: int = 1
    backoff_base: float = 0.5
    backoff_max: float = 8.0
    jitter: bool = False
    jitter_ratio: float = 0.1

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1.")
        if self.backoff_base < 0:
            raise ValueError("backoff_base must be non-negative.")
        if self.backoff_max < self.backoff_base:
            raise ValueError("backoff_max must be greater than or equal to backoff_base.")
        if not 0 <= self.jitter_ratio <= 1:
            raise ValueError("jitter_ratio must be between 0 and 1.")

    def backoff_for_attempt(self, attempt_index: int) -> float:
        """Return the delay in seconds before the next retry attempt."""
        delay: float = self.backoff_base * (2 ** attempt_index)
        delay = min(delay, self.backoff_max)
        if not self.jitter or delay == 0:
            return delay
        spread: float = delay * self.jitter_ratio
        jitter: float = (-spread) + ((2 * spread) * random.random())
        return delay + jitter


@dataclass(slots=True)
class TimeoutConfig:
    """Controls request timeout settings for the MAX API client."""

    request_timeout: float = 10.0

    def __post_init__(self) -> None:
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be greater than 0.")
