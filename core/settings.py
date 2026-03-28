from pathlib import Path
from decouple import config, Csv
import dj_database_url
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ===================== SECURITY =====================
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost", cast=Csv())
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
APPLE_CLIENT_ID = config("APPLE_CLIENT_ID", default="")
APPLE_ISSUER = config("APPLE_ISSUER", default="https://appleid.apple.com")

# ===================== APPLICATIONS =====================
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "invitations"
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "django_celery_results",  # ✅ Add this line
    "axes",

]

LOCAL_APPS = [
    "users.apps.UsersConfig",
    "org_structure.apps.OrgStructureConfig",  # <-- Add this line
    "positions.apps.PositionsConfig",  # 👈 add this

    # ✅ Uncomment/add this line
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
AUTH_USER_MODEL = 'users.User'  # ✅ Add this line
# Use our custom Invitation model
INVITATIONS_INVITATION_MODEL = 'users.Invitation'
# Number of days before an invitation link expires
INVITATIONS_INVITATION_EXPIRY = config("INVITATION_EXPIRY_DAYS", default=2, cast=int)
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ===================== MIDDLEWARE =====================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

# ===================== DATABASE =====================
DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL"),
        conn_max_age=600,
    )
}

# ===================== TEMPLATES =====================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ===================== STATIC & MEDIA =====================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===================== AUTH =====================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
PASSWORD_RESET_TIMEOUT = config(
    "PASSWORD_RESET_TIMEOUT",
    default=60 * 60 * 48,
    cast=int,
)

# ===================== BRUTE FORCE / AXES =====================
AXES_ENABLED = config("AXES_ENABLED", default=True, cast=bool)
AXES_FAILURE_LIMIT = config("AXES_FAILURE_LIMIT", default=5, cast=int)
AXES_COOLOFF_TIME = config("AXES_COOLOFF_TIME", default=1, cast=int)
AXES_LOCK_OUT_AT_FAILURE = config("AXES_LOCK_OUT_AT_FAILURE", default=True, cast=bool)
AXES_RESET_ON_SUCCESS = config("AXES_RESET_ON_SUCCESS", default=True, cast=bool)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]

BRUTE_FORCE_DELAY_THRESHOLD = config("BRUTE_FORCE_DELAY_THRESHOLD", default=3, cast=int)
BRUTE_FORCE_DELAY_MIN_SECONDS = config("BRUTE_FORCE_DELAY_MIN_SECONDS", default=1.0, cast=float)
BRUTE_FORCE_DELAY_MAX_SECONDS = config("BRUTE_FORCE_DELAY_MAX_SECONDS", default=2.0, cast=float)
BRUTE_FORCE_DELAY_WINDOW_SECONDS = config("BRUTE_FORCE_DELAY_WINDOW_SECONDS", default=3600, cast=int)
BRUTE_FORCE_LOCKOUT_NOTIFY_THRESHOLD = config(
    "BRUTE_FORCE_LOCKOUT_NOTIFY_THRESHOLD", default=2, cast=int
)
BRUTE_FORCE_LOCKOUT_NOTIFY_WINDOW_SECONDS = config(
    "BRUTE_FORCE_LOCKOUT_NOTIFY_WINDOW_SECONDS", default=86400, cast=int
)

# ===================== INTERNATIONALIZATION =====================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ===================== CORS =====================
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")

# ===================== REST FRAMEWORK =====================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        # "rest_framework.permissions.AllowAny",  # <--- changed from IsAuthenticated

    ],
    # Use your custom exception handler
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    # Use standardized pagination
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
}


# ===================== JWT =====================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ===================== EMAIL =====================
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=f"MyProject <{EMAIL_HOST_USER}>",
)
ROOT_URLCONF = "core.urls"

# ===================== REDIS / CACHE =====================
REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ===================== CELERY =====================
CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL",
    default=REDIS_URL,
)

CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ===================== LOGGING =====================
LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "django.log",
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}
