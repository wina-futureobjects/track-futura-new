"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Completely disable DataDog tracing before any other imports
os.environ['DD_TRACE_ENABLED'] = 'false'
os.environ['DD_PROFILING_ENABLED'] = 'false'
os.environ['DD_APM_ENABLED'] = 'false'
os.environ['DD_LOGS_ENABLED'] = 'false'
os.environ['DD_TRACE_STARTUP_LOGS'] = 'false'
os.environ['_DD_TRACE_ENABLED'] = 'false'
os.environ['DATADOG_TRACE_ENABLED'] = 'false'

# Block ddtrace imports completely
sys.modules['ddtrace'] = None
sys.modules['ddtrace.profiling'] = None
sys.modules['ddtrace.profiling.scheduler'] = None

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
