# ruff: noqa: F401


def test_import():
    import fastlimits


def test_import_modules():
    from fastlimits import (
        BaseLimiterDependency,
        RateLimitExceeded,
        RateLimitingMiddleware,
        limit,
    )
