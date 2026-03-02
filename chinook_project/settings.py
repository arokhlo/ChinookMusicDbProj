import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== SECURITY SETTINGS =====
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# UPDATED: ALLOWED_HOSTS using environment variable with Heroku support
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,.herokuapp.com').split(',')

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

# ===== APPLICATION DEFINITION =====
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party apps
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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
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
        'DIRS': [
            BASE_DIR / 'templates',  # Project-level templates
        ],
        'APP_DIRS': True,  # This is sufficient for both development and production
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'chinook_app.context_processors.site_settings',
            ],
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'chinook_project.wsgi.application'

# ===== DATABASE CONFIGURATION =====
# UPDATED: Simplified database configuration with proper Heroku support
import dj_database_url

# Default database URL from environment or SQLite fallback
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Use the provided DATABASE_URL (Heroku or custom)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
    # Force SSL for PostgreSQL on Heroku
    if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
else:
    # Default to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,  # Increase timeout for better concurrency
            }
        }
    }

# ===== PASSWORD VALIDATION =====
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===== INTERNATIONALIZATION =====
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===== STATIC FILES =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Development static files
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Production static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===== MEDIA FILES =====
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT / 'avatars', exist_ok=True)

# ===== DEFAULT PRIMARY KEY =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== AUTHENTICATION BACKENDS =====
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ===== DJANGO ALLAUTH CONFIGURATION =====
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_GET = True
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SESSION_REMEMBER = True  # Remember login sessions
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True  # Password confirmation

# ===== CRISPY FORMS CONFIGURATION =====
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ===== EMAIL CONFIGURATION =====
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR / 'emails'  # Directory for file-based emails
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@chinookmusic.com')

# ===== SESSION CONFIGURATION =====
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'chinook_sessionid'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===== CACHE CONFIGURATION =====
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ===== FILE UPLOAD CONFIGURATION =====
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
AVATAR_MAX_SIZE = 2 * 1024 * 1024
AVATAR_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

# ===== CUSTOM SETTINGS =====
SITE_NAME = "Chinook Music Database"
SITE_DESCRIPTION = "Explore and manage your music collection"
SITE_URL = "http://localhost:8000" if DEBUG else os.environ.get('SITE_URL', 'https://chinookmusicdbpro-9cf6a74ba2e3.herokuapp.com')

# ===== ERROR HANDLING & LOGGING =====
if DEBUG:
    DEBUG_PROPAGATE_EXCEPTIONS = True
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'debug.log',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
            'chinook_app': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG' if DEBUG else 'INFO',
                'propagate': False,
            },
        },
    }
else:
    DEBUG_PROPAGATE_EXCEPTIONS = False
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'errors.log',
                'formatter': 'verbose',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }

# ===== SECURITY HEADERS (Production) =====
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ===== PERFORMANCE OPTIMIZATIONS =====
if 'postgresql' in DATABASES['default'].get('ENGINE', ''):
    DATABASES['default']['CONN_MAX_AGE'] = 60

WHITENOISE_MANIFEST_STRICT = False

if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# ===== DJANGO DEBUG TOOLBAR (Development Only) =====
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
        
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: True,
            'SHOW_TEMPLATE_CONTEXT': True,
        }
    except ImportError:
        pass

# ===== FINAL SETUP CHECKS =====
for directory in [STATIC_ROOT, MEDIA_ROOT, BASE_DIR / 'templates', BASE_DIR / 'emails']:
    os.makedirs(directory, exist_ok=True)

print(f"✅ Settings loaded: DEBUG={DEBUG}, ALLOWED_HOSTS={ALLOWED_HOSTS}")