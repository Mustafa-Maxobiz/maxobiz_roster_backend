# Bokado Backend (Django)

Bokado is a Django + DRF backend scaffold with JWT auth, standardized API responses, pagination, CORS, and Celery wiring. It includes a small `common` utilities package and a stub `users` app.

## Stack

- Python 3.12
- Django 5.2
- Django REST Framework
- SimpleJWT (token auth)
- Celery + django-celery-beat + django-celery-results
- PostgreSQL (via `DATABASE_URL`)

## Project Layout

- `core/` Django project settings, URLs, ASGI/WSGI
- `common/` API response wrapper, pagination, permissions, exceptions, mixins
- `users/` stub Django app (not enabled by default)
- `manage.py` Django management entry point

## Features Included

- Standardized API responses via `common.responses.APIResponse`
- Global DRF exception handler (`common.exceptions.custom_exception_handler`)
- Page-number pagination with meta wrapper (`common.pagination.StandardResultsSetPagination`)
- Per-action permissions mixin for ViewSets (`common.mixins.PermissionPerActionMixin`)
- Role-based permissions helpers (`common.permissions.*`)
- JWT authentication defaults via SimpleJWT
- CORS + CSRF trusted origins from environment
- Celery configuration (broker + results backend)

## Setup

### 1) Install dependencies

```bash
poetry install
```

### 1.1) Poetry package management

Install a runtime dependency:

```bash
poetry add somepackage
```

Install a dev dependency:

```bash
poetry add --group dev thatpkg
```

List installed packages:

```bash
poetry show
```

### 2) Configure environment

Copy `.env-example` to `.env` and fill values.

Key variables:

- `SECRET_KEY`
- `DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `EMAIL_*`
- `CELERY_BROKER_URL`

Note: `core/settings.py` uses `decouple` and `dj_database_url`. If you see import errors, add these packages to your environment.

### 3) Run migrations

```bash
poetry run python manage.py migrate
```

### 4) Run server

```bash
poetry run python manage.py runserver
```

Admin UI will be at `http://localhost:8000/admin/`.

### Poetry shell workflow

You can also enter the Poetry shell and run Django commands without `poetry run`:

```bash
poetry shell
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
```

## Celery

Celery is configured to use the broker from `CELERY_BROKER_URL` and store results in Django DB via `django-celery-results`.

If you add tasks, run a worker like:

```bash
poetry run celery -A core worker -l info --pool=solo
```

If you use `django-celery-beat`, run the beat scheduler:

```bash
poetry run celery -A core beat -l info
```

## Users App

The `users` app is currently a stub and is not enabled. To enable it, add `"users"` to `LOCAL_APPS` in `core/settings.py`.

## Error Handling Guidelines

Use standardized error handling to keep responses consistent across apps:

- For input/validation errors, use the helper:
  - `from common.errors import raise_validation_error`
  - Example: `raise_validation_error("Email is required", field="email")`
- For auth/permission/404 cases, raise DRF exceptions:
  - `AuthenticationFailed`, `PermissionDenied`, `NotFound`
- Do not manually build error `APIResponse` in views/services.
- Success responses should still use `APIResponse`.

### Template Snippet (New Views)

```python
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, NotFound
from common.errors import raise_validation_error
from common.responses import APIResponse

def post(self, request, *args, **kwargs):
    if not request.data.get("email"):
        raise_validation_error("Email is required", field="email")

    # ... your logic here ...

    if not user:
        raise AuthenticationFailed("Invalid credentials")

    return APIResponse(success=True, message="OK", data={})
```

## Testing

```bash
poetry run pytest
```

## Formatting

```bash
poetry run black .
poetry run isort .
```

## API Response Shape

Most API responses are wrapped like:

```json
{
  "success": true,
  "message": "...",
  "data": {},
  "errors": null
}
```

Paginated responses include a `meta` block:

```json
{
  "success": true,
  "message": "List fetched successfully",
  "data": {
    "items": [],
    "meta": {
      "count": 0,
      "page": 1,
      "page_size": 10,
      "total_pages": 0
    }
  },
  "errors": null
}
```

## Notes

- Default DRF permission is `IsAuthenticated`. Update `REST_FRAMEWORK` in `core/settings.py` if you want public endpoints.
- JWT access tokens default to 7 days, refresh tokens to 30 days.
