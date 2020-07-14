from .base import *

DEBUG = True

ALLOWED_HOSTS = []

# internal ips for debug toolbar
INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# debu toolbar settings
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPTS_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar
}

STRIPE_SECRET_KEY = "sk_test_51H4rD4LJl9q7YS6eXisKhIoj6NgmYv4Qznj5sQxixOontUYcAEcnKDPKDpKhFYBnFY1XypWM2CDZmyU8qLt7CFad00w91wYsrp"
