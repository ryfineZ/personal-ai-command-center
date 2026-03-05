"""
Personal AI Command Center - Helper Functions
"""
from typing import Optional

# NOTE: User Authentication
# The current implementation uses JWT tokens for authentication.
# The get_current_user dependency in auth.py handles token validation.
# This helper function provides a fallback for internal/service operations
# that may not have a user context (e.g., background tasks, webhooks).
# For production, consider implementing:
# - OAuth2 integration (Google, GitHub, etc.)
# - Role-based access control (RBAC)
# - API key authentication for services
# - Session management with refresh tokens

def get_current_user_id() -> int:
    """Get the current user ID from auth context"""
    # For now, return default user ID
    # In production, this should get the user ID from the auth token
    return 1

def get_user_id_from_auth(user: Optional[dict] = None) -> int:
    """Get user ID from auth user object or return default"""
    if user and hasattr(user, 'id'):
        return user.id
    return 1
