"""
Deprecation middleware for v1 API responses.

Adds RFC 8594-compliant deprecation headers to every response from v1 routes:
  - Deprecation: true
  - Sunset: <ISO date when v1 will be removed>
  - Link: <migration guide URL>

Also injects a _deprecation_warning field into JSON response bodies so
developers reading raw API responses are immediately informed.
"""
from datetime import datetime, timezone
from functools import wraps

from flask import current_app, g, jsonify, make_response, request


def deprecation_headers(response, sunset_date: str):
    """Attach RFC 8594 deprecation headers to an existing Response object."""
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = sunset_date
    response.headers["Link"] = (
        '</api/v2/payments>; rel="successor-version", '
        '<https://docs.example.com/migration/v1-to-v2>; rel="deprecation"'
    )
    response.headers["Warning"] = (
        '299 - "This API version is deprecated. '
        f'Please migrate to /api/v2/payments before {sunset_date}."'
    )
    return response


def inject_deprecation_warning(data: dict, sunset_date: str) -> dict:
    """Add a _deprecation_warning key to a JSON response dict."""
    data["_deprecation_warning"] = {
        "message": "This API version (v1) is deprecated and will be removed on "
        f"{sunset_date}. Please migrate to /api/v2/payments.",
        "sunset_date": sunset_date,
        "migration_guide": "https://docs.example.com/migration/v1-to-v2",
        "successor": "/api/v2/payments",
    }
    return data


def register_deprecation_after_request(app, blueprint_name: str):
    """
    Register an after_request hook scoped to a specific blueprint.

    Flask does not support per-blueprint after_request for non-error responses
    natively in older patterns, so we register on the app and filter by
    request.blueprintname.
    """

    @app.after_request
    def add_v1_deprecation_headers(response):
        if request.blueprints and blueprint_name in request.blueprints:
            sunset = current_app.config.get("API_V1_SUNSET_DATE", "2026-12-31")
            response = deprecation_headers(response, sunset)
        return response
