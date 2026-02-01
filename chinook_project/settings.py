import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== SECURITY SETTINGS =====
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-chinook-secret-key-2024'
)
DEBUG = True

ALLOWED_HOSTS = [
    'chinookmusicdbpro.herokuapp.com',
    'localhost',
    '127.0.0.1',
    '.herokuapp.com'
]

# ===== APPLICATION DEFINITION =====
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'django_extensions',
    'allauth',
    'allauth.account',
    'crispy_forms',
    'crispy_bootstrap5',

    # Local apps
    'chinook_app',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'chinook_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chinook_project.wsgi.application'

# ===== DATABASE CONFIGURATION =====
if 'DATABASE_URL' in os.environ:
    # Production database (PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'alive_smell_rank_585650',
            'USER': 'neondb_owner',
            'PASSWORD': 'npg_FgsZR9MWb8Sr',
            'HOST': 'ep-long-dust-aggdj4tj.c-2.eu-central-1.aws.neon.tech',
            'PORT': '5432',
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===== PASSWORD VALIDATION =====
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

# ===== INTERNATIONALIZATION =====
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===== STATIC FILES =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

# ===== MEDIA FILES =====
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===== DEFAULT PRIMARY KEY =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== AUTHENTICATION BACKENDS =====
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ===== EMAIL CONFIGURATION =====
# Enable email for admin notifications but disable for password reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get(
    'EMAIL_HOST_USER', 'your-email@gmail.com'
)
EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD', 'your-app-password'
)

# Default from email
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL', 'noreply@chinookmusic.com'
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [
    ('Admin', os.environ.get(
        'ADMIN_EMAIL', 'admin@chinookmusic.com'
    )),
]

# ===== DJANGO ALLAUTH CONFIGURATION =====
# Use security questions instead of email for password reset
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Security question password reset settings
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Chinook Music] '

# Custom forms for allauth - USE SECURITY QUESTION SYSTEM
ACCOUNT_FORMS = {
    'signup': 'chinook_app.forms.CustomSignupForm',
    'login': 'chinook_app.forms.CustomLoginForm',
    'reset_password': 'chinook_app.forms.CustomResetPasswordForm',
    'reset_password_from_key': 'chinook_app.forms.CustomResetPasswordKeyForm',
}

# ===== CRISPY FORMS CONFIGURATION =====
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ===== MESSAGE STORAGE =====
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# ===== SECURITY SETTINGS FOR PRODUCTION =====
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# Add this to override security settings in development
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False



# In settings.py, modify the STATICFILES_STORAGE section
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ===== LOGGING CONFIGURATION =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'chinook_app': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
