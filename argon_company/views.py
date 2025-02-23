import os
import shutil

import psutil
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.mail import get_connection
from django.db import connection
from ninja import Router
from ninja.throttling import AnonRateThrottle

router = Router()


@router.get("/health/", tags=["Health Check"], throttle=[AnonRateThrottle('24/d')])
def health_check(request):
    health_status = {"status": "ok"}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["database_error"] = str(e)

    try:
        cache.set("health_check", "ok", timeout=1)
        if cache.get("health_check") == "ok":
            health_status["cache"] = "available"
        else:
            health_status["cache"] = "unavailable"
    except Exception as e:
        health_status["cache"] = "error"
        health_status["cache_error"] = str(e)

    health_status["debug_mode"] = settings.DEBUG
    health_status["environment"] = os.getenv("DJANGO_ENV", "unknown")
    try:
        mail_conn = get_connection()
        mail_conn.open()
        health_status["email_backend"] = "working"
        mail_conn.close()
    except Exception as e:
        health_status["email_backend"] = "error"
        health_status["email_error"] = str(e)

    total, used, free = shutil.disk_usage("/")
    health_status["disk_space"] = {"total": total, "used": used, "free": free}
    mem = psutil.virtual_memory()
    health_status["memory"] = {"total": mem.total, "available": mem.available, "used": mem.used, "percent": mem.percent}
    health_status["cpu_usage"] = psutil.cpu_percent(interval=1)
    health_status["installed_apps"] = [app.name for app in apps.get_app_configs()]

    try:
        from tasks.models import Task
        health_status["myapp_model_count"] = Task.objects.count()
    except Exception as e:
        health_status["myapp_model_error"] = str(e)

    return health_status
