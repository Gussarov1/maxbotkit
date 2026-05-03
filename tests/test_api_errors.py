from maxbotkit.exceptions.api import (
    APIError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)


def test_api_error_from_response_selects_specific_subclass() -> None:
    assert isinstance(APIError.from_response(400, {"message": "bad"}), BadRequestError)
    assert isinstance(APIError.from_response(401, {"message": "auth"}), UnauthorizedError)
    assert isinstance(APIError.from_response(403, {"message": "forbidden"}), ForbiddenError)
    assert isinstance(APIError.from_response(404, {"message": "missing"}), NotFoundError)
    assert isinstance(APIError.from_response(429, {"message": "slow down"}), RateLimitError)
    assert isinstance(APIError.from_response(500, {"message": "boom"}), ServerError)


def test_api_error_from_response_uses_fallback_text() -> None:
    error = APIError.from_response(418, None)

    assert error.status_code == 418
    assert error.message == "Unknown API error"
