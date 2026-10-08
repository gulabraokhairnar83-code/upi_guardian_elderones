"""UPI Guardian - Standard JSON Response Helpers."""

from flask import jsonify, Response


def json_response(data: any, status_code: int = 200) -> tuple[Response, int]:
    """Helper returning JSON response with status code."""
    return jsonify(data), status_code
