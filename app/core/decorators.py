"""
Decoradores para la aplicación.
"""

import time
from functools import wraps
from flask import request, jsonify

# Rate limiting simple
request_times = {}
RATE_LIMIT = 60  # requests per minute
RATE_WINDOW = 60  # seconds


def rate_limit_decorator(f):
    """Decorador para rate limiting."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
        current_time = time.time()

        # Limpiar requests antiguos
        if client_ip in request_times:
            request_times[client_ip] = [
                t for t in request_times[client_ip] if current_time - t < RATE_WINDOW
            ]
        else:
            request_times[client_ip] = []

        # Verificar límite
        if len(request_times[client_ip]) >= RATE_LIMIT:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Rate limit excedido. Intenta más tarde.",
                        "retry_after": 60,
                        "error_code": "RATE_LIMIT_EXCEEDED",
                    }
                ),
                429,
            )

        request_times[client_ip].append(current_time)
        return f(*args, **kwargs)

    return decorated_function
