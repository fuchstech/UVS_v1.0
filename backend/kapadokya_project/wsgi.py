"""
WSGI config for kapadokya_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kapadokya_project.settings')

application = get_wsgi_application()
