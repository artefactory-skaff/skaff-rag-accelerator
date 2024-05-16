from backend.api_plugins.insecure_authentication.insecure_authentication import (
    insecure_authentication_routes,
)
from backend.api_plugins.secure_authentication.secure_authentication import (
    authentication_routes,
)
from backend.api_plugins.sessions.sessions import session_routes

__all__ = [
    "insecure_authentication_routes",
    "authentication_routes",
    "session_routes",
]
