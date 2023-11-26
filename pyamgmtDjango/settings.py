import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR: os.path.abspath(BASE_DIR)  # Helper for PyCharm

# SECURITY WARNING: keep the secret key used in production secret!
with open(BASE_DIR / 'etc' / 'sk.txt') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.User'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'var' / 'tmp' / 'django_cache'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'var' / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    # Django bundled
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'debug_toolbar',
    # Local Dependencies
    'django_base',
    'ccbv',
    'schemaviz',
    # Local Apps
    # 'base',
    'accounts',
    'core',
    'sandbox',
]

INTERNAL_IPS = ['127.0.0.1']

LANGUAGE_CODE = 'en-us'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "{levelname} {asctime} {message}",
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    },
    # From the docs
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        }
    }
}

LOGIN_REDIRECT_URL = '/'

MEDIA_ROOT = BASE_DIR / 'var' / 'media'

MEDIA_URL = '/media/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Third-party
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'pyamgmtDjango.urls'

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': ['django_base.builtins'],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

WSGI_APPLICATION = 'pyamgmtDjango.wsgi.application'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Non-standard options

# ASSET_URL: str = '/assets/'
ASSET_URL: str = 'http://localhost:1235/assets/'

STATIC_RESOURCES = {}

VITE_CLIENT_URL = 'http://localhost:1235/assets/@vite/client'

VITE_URL: str = 'assets/'

if DEBUG:
    # import mimetypes
    # mimetypes.add_type('application/javascript', '.js', True)
    TEMPLATES[0]['OPTIONS']['string_if_invalid'] = '[INVALID %s]'
