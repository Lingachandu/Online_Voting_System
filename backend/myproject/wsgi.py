import os
import sys
from pathlib import Path

# Add backend directory to sys.path so django can import apps
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()