# myproject/celery.py

from celery import Celery
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'try.settings')

app = Celery('try')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
