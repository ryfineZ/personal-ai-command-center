"""
Personal AI Command Center - Helper Functions
"""
from typing import Optional

# Temporary: Return default user ID until full auth is implemented
# TODO: Implement proper user authentication
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
