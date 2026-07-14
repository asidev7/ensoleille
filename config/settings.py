"""
Settings — Rédaction Ensoleillé — La Presse.
« Ensoleillé, lumière sur l'obscurité ! »
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    SECRET_KEY=(str, "django-insecure-dev-only-change-me"),
    DATABASE_URL=(str, ""),
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
if DEBUG:
    ALLOWED_HOSTS = ALLOWED_HOSTS + ["*"]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    # Apps Ensoleillé
    "apps.core",
    "apps.articles",
    "apps.comments",
    "apps.ads",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.parametres_site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de données : PostgreSQL si DATABASE_URL fourni, sinon SQLite (dev) ---
if env("DATABASE_URL"):
    DATABASES = {"default": env.db("DATABASE_URL")}
    POSTGRES = DATABASES["default"]["ENGINE"].endswith("postgresql")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    POSTGRES = False

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation ---
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Porto-Novo"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques & médias ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth dashboard ---
LOGIN_URL = "dashboard:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "dashboard:login"

EMAIL_BACKEND = env("EMAIL_BACKEND")

# --- Cache (fragments / listes) ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# --- Sécurité production (activée quand DEBUG=False) ---
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# --- Jazzmin (thème admin Django) ---
JAZZMIN_SETTINGS = {
    "site_title": "Ensoleillé Admin",
    "site_header": "Ensoleillé",
    "site_brand": "Ensoleillé",
    "site_logo": "img/logo-ensoleille.png",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Bienvenue dans l'administration Ensoleillé",
    "copyright": "Ensoleillé",
    "search_model": ["articles.Article"],
    "show_ui_builder": False,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "articles.Article": "fas fa-newspaper",
        "articles.Categorie": "fas fa-folder",
        "articles.Tag": "fas fa-tags",
        "articles.Auteur": "fas fa-pen-nib",
        "comments.Commentaire": "fas fa-comments",
        "ads.Publicite": "fas fa-ad",
        "ads.AdSenseConfig": "fab fa-google",
        "core.ParametresSite": "fas fa-cogs",
        "core.AbonneNewsletter": "fas fa-envelope",
        "core.MessageContact": "fas fa-envelope-open-text",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark",
    "accent": "accent-warning",
    "sidebar": "sidebar-dark-warning",
    "brand_colour": "navbar-dark",
    "no_navbar_border": True,
    "sidebar_nav_flat_style": True,
}
