# common/responses.py
from rest_framework.response import Response

class APIResponse(Response):
    def __init__(
        self,
        *,
        success=True,
        message="",
        data=None,
        errors=None,
        code=None,
        status=None
    ):
        response_data = {
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
        }
        if code:
            response_data["errors"] = response_data.get("errors") or {}
            response_data["errors"]["code"] = code

        super().__init__(response_data, status=status)
