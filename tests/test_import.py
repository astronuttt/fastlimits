# ruff: noqa: F401


def test_import():
    import fastlimiter


def test_import_modules():
    from fastlimiter import (
        BaseLimiterDependency,
        RateLimitExceeded,
        RateLimitingMiddleware,
        limit,
    )
