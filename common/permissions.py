from rest_framework import permissions

class AdminOnlyPermission(permissions.BasePermission):
    """Allow access only to Admin users."""
    message = "Only Admin users are allowed."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class CustomerOnlyPermission(permissions.BasePermission):
    """Allow access only to Customer users."""
    message = "Only Customer users are allowed."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "customer"


class AdminCustomerPermission(permissions.BasePermission):
    """Allow access to Admin or Customer users."""
    message = "Only Admin & Customer users are allowed."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "customer"]
