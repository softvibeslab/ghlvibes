"""FastAPI dependency injection utilities.

This module provides common dependencies for authentication,
authorization, and other cross-cutting concerns.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt

from src.core.config import settings


class CurrentUser:
    """Represents the currently authenticated user.

    This class holds user information extracted from the JWT token.
    """

    def __init__(
        self,
        user_id: UUID,
        account_id: UUID,
        email: str,
        roles: list[str],
    ) -> None:
        """Initialize current user.

        Args:
            user_id: Unique identifier for the user.
            account_id: Account/tenant the user belongs to.
            email: User's email address.
            roles: List of roles assigned to the user.
        """
        self.user_id = user_id
        self.account_id = account_id
        self.email = email
        self.roles = roles

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role.

        Args:
            role: Role name to check.

        Returns:
            True if user has the role, False otherwise.
        """
        return role in self.roles

    def has_any_role(self, roles: list[str]) -> bool:
        """Check if user has any of the specified roles.

        Args:
            roles: List of role names to check.

        Returns:
            True if user has at least one of the roles.
        """
        return any(role in self.roles for role in roles)


async def get_current_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    """Extract and validate current user from JWT token.

    This dependency extracts the JWT from the Authorization header,
    validates it, and returns the current user information.

    Args:
        request: FastAPI request object.
        authorization: Authorization header value.

    Returns:
        CurrentUser: The authenticated user.

    Raises:
        HTTPException: If token is missing, invalid, or expired.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Extract user info from payload
    user_id = payload.get("sub")
    account_id = payload.get("account_id")
    email = payload.get("email")
    roles = payload.get("roles", [])

    if not all([user_id, account_id, email]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        user_id=UUID(user_id),
        account_id=UUID(account_id),
        email=email,
        roles=roles,
    )


# Type alias for dependency injection
AuthenticatedUser = Annotated[CurrentUser, Depends(get_current_user)]


class PermissionChecker:
    """Dependency class for checking user permissions.

    Use as a dependency to ensure users have required roles.
    """

    def __init__(self, required_roles: list[str]) -> None:
        """Initialize permission checker.

        Args:
            required_roles: List of roles required for access.
        """
        self.required_roles = required_roles

    async def __call__(self, user: AuthenticatedUser) -> CurrentUser:
        """Check if user has required permissions.

        Args:
            user: The authenticated user.

        Returns:
            The user if they have required permissions.

        Raises:
            HTTPException: If user lacks required permissions.
        """
        if not user.has_any_role(self.required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


def require_roles(*roles: str) -> Any:
    """Create a dependency that requires specific roles.

    Args:
        roles: Role names required for access.

    Returns:
        A dependency that validates user roles.
    """
    return Depends(PermissionChecker(list(roles)))
