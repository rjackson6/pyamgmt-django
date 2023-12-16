import os
from pathlib import Path

from . import env

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env.DEBUG

SECRET_KEY = env.SECRET_KEY

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
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{env.REDIS_HOST}:{env.REDIS_PORT}'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.DATABASE_NAME,
        'USER': env.DATABASE_USER,
        'PASSWORD': env.DATABASE_PASSWORD,
        'HOST': env.DATABASE_HOST,
        'PORT': env.DATABASE_PORT,
    },
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
    'django_ccbv',
    'schemaviz',
    # Local Apps
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

# env
MEDIA_ROOT = BASE_DIR / 'var' / 'media'

# env
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

ROOT_URLCONF = 'pyamgmt.urls'

SECURE_CROSS_ORIGIN_OPENER_POLICY = env.SECURE_CROSS_ORIGIN_OPENER_POLICY

if DEBUG:
    SECURE_REFERRER_POLICY = None

# env
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

WSGI_APPLICATION = 'pyamgmt.wsgi.application'

X_FRAME_OPTIONS = 'SAMEORIGIN'

######################
# Non-standard options
######################

ARANGO_HOST = env.ARANGO_HOST
ARANGO_PORT = env.ARANGO_PORT
ARANGO_URL = f'{ARANGO_HOST}:{ARANGO_PORT}/'

ASSET_URL = env.ASSET_URL

STATIC_RESOURCES = {}

VITE_CLIENT_URL = env.VITE_CLIENT_URL if DEBUG else ''

VITE_URL: str = 'assets/'

if DEBUG:
    # import mimetypes
    # mimetypes.add_type('application/javascript', '.js', True)
    TEMPLATES[0]['OPTIONS']['string_if_invalid'] = '[INVALID %s]'
