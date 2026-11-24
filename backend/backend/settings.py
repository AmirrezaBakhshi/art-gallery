import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_list(name, default=""):
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


def env_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


DEBUG = env_bool("DJANGO_DEBUG", "false")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY == "dev-only-change-me-before-deployment":
    raise RuntimeError("DJANGO_SECRET_KEY must be set to a unique, secret value.")
if not DEBUG and (
    len(SECRET_KEY) < 50
    or SECRET_KEY.startswith(("local-development-only", "replace-with-", "dev-only"))
):
    raise RuntimeError("Set a unique, randomly generated DJANGO_SECRET_KEY of at least 50 characters in production.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise RuntimeError("Set DJANGO_ALLOWED_HOSTS to the hostnames serving this application.")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "corsheaders", "artgallery",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_COOKIE_SAMESITE", "Lax")
GALLERY_SESSION_TTL_DAYS = int(os.getenv("GALLERY_SESSION_TTL_DAYS", "14"))
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

ROOT_URLCONF = "backend.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "backend.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DEBUG and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must point to PostgreSQL when DJANGO_DEBUG is false.")
if DATABASE_URL:
    if not DATABASE_URL.startswith(("postgres://", "postgresql://")):
        raise RuntimeError("DATABASE_URL must use PostgreSQL (postgres:// or postgresql://).")
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG)}
else:
    # SQLite is a convenient local-development default only.
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "artgallery.authentication.GalleryTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_RATES": {
        "gallery_login": os.getenv("GALLERY_LOGIN_RATE", "5/minute"),
        "gallery_signup": os.getenv("GALLERY_SIGNUP_RATE", "3/hour"),
    },
}

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", "true")
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_HSTS_INCLUDE_SUBDOMAINS", "false")
    SECURE_HSTS_PRELOAD = env_bool("DJANGO_HSTS_PRELOAD", "false")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
    if env_bool("DJANGO_TRUST_PROXY_SSL_HEADER", "false"):
        # Enable only when a trusted reverse proxy overwrites X-Forwarded-Proto.
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
