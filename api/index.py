"""Vercel serverless entry point — exposes the Django WSGI app as `app`."""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oasis.settings")

from oasis.wsgi import application as app  # noqa: E402
