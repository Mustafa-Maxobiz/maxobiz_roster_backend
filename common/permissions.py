from rest_framework import permissions


def _has_role(user, roles):
    return user.is_authenticated and user.role in roles


class AdminOnlyPermission(permissions.BasePermission):
    """Allow access only to Admin users."""
    message = "Only Admin users are allowed."

    def has_permission(self, request, view):
        return _has_role(request.user, ["admin"])


class HROnlyPermission(permissions.BasePermission):
    """Allow access only to HR users."""
    message = "Only HR users are allowed."

    def has_permission(self, request, view):
        return _has_role(request.user, ["hr"])


class EMPOnlyPermission(permissions.BasePermission):
    """Allow access only to EMP users."""
    message = "Only EMP users are allowed."

    def has_permission(self, request, view):
        return _has_role(request.user, ["emp"])


class AdminEMPPermission(permissions.BasePermission):
    """Allow access to Admin or EMP users."""
    message = "Only Admin & EMP users are allowed."

    def has_permission(self, request, view):
        return _has_role(request.user, ["admin", "emp"])


class CustomerOnlyPermission(EMPOnlyPermission):
    """Deprecated: use EMPOnlyPermission."""


class AdminCustomerPermission(AdminEMPPermission):
    """Deprecated: use AdminEMPPermission."""
