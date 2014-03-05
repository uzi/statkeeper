"""
Django settings for statkeeper project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SITE_ID = 1

APP_NAME = "Stat Keeper"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '[FIXME FIXME FIXME -- MAKE ME SOMETHING UNIQUE]'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'pipeline',
    'match',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'match.middleware.RestrictAdminToStaffMiddleware',
)

APP_NAME = 'statkeeper'
ROOT_URLCONF = '%s.urls' % APP_NAME

WSGI_APPLICATION = '%s.wsgi.application' % APP_NAME


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '%s.db' % APP_NAME),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "match.template_processor.app_data",
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# XXX Want to use this one, but it isn't jiving at the moment
#STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

PIPELINE_CSS = {
    'app': {
        'source_filenames': (
            'match/css/*.css',
            'match/css/*.less',
        ),
        'output_filename': 'match/css/app.css',
    },
}

PIPELINE_JS = {
    'app': {
        'source_filenames': (
            'match/js/contrib/jquery-1.11.0.js',
            'match/js/contrib/underscore.js',
            'match/js/contrib/bootstrap.js',
            'match/js/custom/*.js',
        ),
        'output_filename': 'match/js/app.js',
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.less.LessCompiler',
)
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'

NODE_DIR = os.path.join(BASE_DIR, 'node_modules')
PIPELINE_YUGLIFY_BINARY = os.path.join(NODE_DIR, 'yuglify', 'bin', 'yuglify')
PIPELINE_LESS_BINARY = os.path.join(NODE_DIR, 'less', 'bin', 'lessc')

try:
    execfile(os.path.join(BASE_DIR, APP_NAME, 'localsettings.py'))
except IOError:
    pass
