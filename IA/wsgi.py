"""
WSGI config for IA project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""


from django.core.wsgi import get_wsgi_application
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'IA.settings'

path = '/home/saintmaur/saintmaur.pythonanywhere.com'
if path not in sys.path:
    sys.path.insert(0, path)

application = get_wsgi_application()
