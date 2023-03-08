"""
WSGI config for IA project.
"""


from django.core.wsgi import get_wsgi_application
import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'IA.settings'

path = '/home/saintmaur/saintmaur.pythonanywhere.com'
if path not in sys.path:
    sys.path.insert(0, path)

application = get_wsgi_application()
