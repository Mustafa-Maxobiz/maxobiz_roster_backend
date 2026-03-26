
# common/exceptions.py
from rest_framework.views import exception_handler
from rest_framework import status
from common.responses import APIResponse
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied, NotFound

ERROR_CODES = {
    ValidationError: "VALIDATION_ERROR",
    AuthenticationFailed: "AUTHENTICATION_FAILED",
    PermissionDenied: "PERMISSION_DENIED",
    NotFound: "NOT_FOUND",
}

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        code = ERROR_CODES.get(type(exc), "ERROR")
        message = getattr(exc, "detail", str(exc))
        errors = getattr(response, "data", None)

        # Wrap code inside errors
        if isinstance(errors, dict):
            errors = {
                "code": code,
                "fields": errors
            }

        return APIResponse(
            success=False,
            message=str(message),
            data=None,
            code=None,
            status=response.status_code,
            errors=errors
        )

    # Fallback for unhandled exceptions
    return APIResponse(
        success=False,
        message="Internal server error",
        data=None,
        code=None,
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors={
            "code": "INTERNAL_SERVER_ERROR",
            "message": str(exc)
        }
    )

