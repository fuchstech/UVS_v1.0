# This file tells Python that kapadokya_project directory is a Python package

# This will make sure the app is always imported when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
