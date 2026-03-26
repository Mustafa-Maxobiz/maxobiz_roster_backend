from rest_framework.exceptions import ValidationError


def to_error_dict(detail, field="detail"):
    if isinstance(detail, dict):
        return detail
    if isinstance(detail, (list, tuple)):
        return {field: list(detail)}
    return {field: str(detail)}


def raise_validation_error(detail, field="detail"):
    raise ValidationError(to_error_dict(detail, field=field))
