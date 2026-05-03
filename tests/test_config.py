from __future__ import annotations

from unittest.mock import patch

import pytest

from maxbotkit import RetryConfig, TimeoutConfig


def test_retry_config_validates_inputs() -> None:
    with pytest.raises(ValueError):
        RetryConfig(attempts=0)

    with pytest.raises(ValueError):
        RetryConfig(jitter_ratio=1.5)


def test_retry_config_exponential_backoff_without_jitter() -> None:
    config = RetryConfig(attempts=3, backoff_base=0.5, backoff_max=8.0)

    assert config.backoff_for_attempt(0) == 0.5
    assert config.backoff_for_attempt(1) == 1.0
    assert config.backoff_for_attempt(10) == 8.0


def test_retry_config_applies_jitter() -> None:
    config = RetryConfig(
        attempts=2,
        backoff_base=1.0,
        backoff_max=8.0,
        jitter=True,
        jitter_ratio=0.1,
    )

    with patch("maxbotkit.config.random.uniform", return_value=0.05):
        assert config.backoff_for_attempt(0) == 1.05


def test_timeout_config_validates_request_timeout() -> None:
    with pytest.raises(ValueError):
        TimeoutConfig(request_timeout=0)
