"""Dev-server launcher that honors the PORT env var (used by the preview harness)."""
import os
import sys

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    port = os.environ.get('PORT', '8010')
    execute_from_command_line([sys.argv[0], 'runserver', f'0.0.0.0:{port}'])
