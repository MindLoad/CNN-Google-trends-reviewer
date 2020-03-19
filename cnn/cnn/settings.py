import os
import kombu
from datetime import timedelta
from celery.schedules import crontab
from pathlib import Path
from kombu import Queue, Exchange

BASE_DIR = Path(__file__).resolve(strict=True).parents[1]

SECRET_KEY = os.getenv('DJANGO_KEY', '5#3_--@efvk4zok#@27c8hzv6wjrqfw6$*$w1j@=wzixbh4gbe')
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web.apps.WebConfig',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cnn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', ],
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
TEMPLATE_ROOT = BASE_DIR / "templates"

WSGI_APPLICATION = 'cnn.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': 5432,
    }
}

# Password validation
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


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = ('static', )
STATIC_URL = '/static/'
STATIC_ROOT = ''

# Set celery errors
CELERY_SEND_TASK_ERROR_EMAILS = False

# CELERY_BROKER_URL = 'redis://redis:6379'  # Redis broker
CELERY_BROKER_URL = 'amqp://admin:rabbitpass@rabbitmq:5672'

# Set result backend
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_REDIS_MAX_CONNECTIONS = 1

# Set celery serializer
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']

# Set celery Queues
CELERY_TASK_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('low', Exchange('low'), routing_key='low'),
)
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'
CELERY_TASK_ROUTES = {
    # -- HIGH PRIORITY QUEUE -- #
    'web.tasks.task_google_trends_parser': {'queue': 'high'},
    'web.tasks.task_cnn_news_parser': {'queue': 'high'},
    # -- LOW PRIORITY QUEUE -- #
    'web.tasks.task_delete_old_records': {'queue': 'low'},
}

# Set celery timezone
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Europe/Kiev'

# Set celery schedule
CELERY_BEAT_SCHEDULE = {
    'task-cnn-news-parser': {
        'task': 'web.tasks.task_cnn_news_parser',
        'schedule': timedelta(seconds=100),
        # 'args': (*args) # if celery task receive args,
    },
    'task-cnn-channels-parser': {
        'task': 'web.tasks.task_cnn_channels_parser',
        'schedule': timedelta(seconds=300),
    },
    'task-google-trends-parser': {
        'task': 'web.tasks.task_google_trends_parser',
        'schedule': timedelta(seconds=200),
    },
    'task-delete-old-records': {
        'task': 'web.tasks.task_delete_old_records',
        'schedule': timedelta(seconds=350),
    },
}
FLOWER_BROKER = 'amqp://user:password@broker:5672'

try:
    from .local_settings import *
except ImportError:
    pass
