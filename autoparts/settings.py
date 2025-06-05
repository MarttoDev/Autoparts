import os
from pathlib import Path

# Agregados para desarrollo:
DEBUG = True  # Asegúrate de que esté en True
ALLOWED_HOSTS = ['*']  # Permite todas las conexiones (solo para desarrollo)
SECURE_SSL_REDIRECT = False  # Desactiva HTTPS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ct#-0hiwb=t@w+c$soke4ryg&zk%15o50$@!6293#og3%-1p0i'

# Ya no hace falta cambiar estas dos, las tienes arriba:
# DEBUG = True
# ALLOWED_HOSTS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'autoapp',
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

ROOT_URLCONF = 'autoparts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directorio donde están tus templates (index.html, etc.)
        'DIRS': [os.path.join(BASE_DIR, 'autoapp', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # Necesario para request en templates
                'django.contrib.auth.context_processors.auth', # Datos de usuario en templates
                'django.contrib.messages.context_processors.messages', # Mensajes de Django

                # <<< NUEVO: Context processor para el carrito, para que esté disponible en todas las plantillas >>>
                'autoapp.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'autoparts.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# <<< NUEVO: Aquí le decimos a Django dónde buscar tus archivos estáticos adicionales (en autoapp/static) >>>
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'autoapp', 'static'),
]


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
