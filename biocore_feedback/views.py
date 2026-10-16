import json
import logging
import os
import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from biocore_feedback.slack import send_to_slack_sync

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    return ip


def check_rate_limit(ip: str, limit_per_minute: int = 10) -> bool:
    cache_key = f"biocore_feedback_ratelimit_{ip}"
    history = cache.get(cache_key) or []
    now = time.time()
    # Filter out requests older than 60 seconds
    history = [ts for ts in history if now - ts < 60]
    if len(history) >= limit_per_minute:
        return False
    history.append(now)
    cache.set(cache_key, history, timeout=60)
    return True


@csrf_exempt
@require_POST
def submit_feedback(request):
    """Receive feedback from <biocore-feedback> widget and forward to Slack."""
    ip = get_client_ip(request)
    limit = getattr(settings, "BIOCORE_FEEDBACK_RATE_LIMIT", 10)
    if not check_rate_limit(ip, limit_per_minute=limit):
        logger.warning("Feedback rate limit exceeded for IP %s", ip)
        return JsonResponse(
            {"detail": "Too many feedback submissions. Please wait a minute before submitting again."},
            status=429,
        )

    # Get Slack webhook URL from settings or environment
    webhook_url = getattr(
        settings,
        "SLACK_WEBHOOK_URL",
        os.environ.get("SLACK_WEBHOOK_URL", ""),
    )
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL is not configured in settings or environment")
        return JsonResponse(
            {"detail": "Slack webhook is not configured on this server."},
            status=503,
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    name = str(data.get("name", "")).strip()
    app_name = str(data.get("app", "")).strip() or "Web App"
    message = str(data.get("message", "")).strip()
    page_url = data.get("page_url")

    if not name:
        return JsonResponse({"detail": "Name is required."}, status=400)
    if not message:
        return JsonResponse({"detail": "Message cannot be empty."}, status=400)
    if len(message) > 4000:
        return JsonResponse({"detail": "Message is too long (maximum 4000 characters)."}, status=400)

    try:
        send_to_slack_sync(
            webhook_url=webhook_url,
            name=name,
            app_name=app_name,
            message=message,
            page_url=page_url,
        )
        logger.info("Feedback sent to Slack successfully for app '%s' from '%s'", app_name, name)
        return JsonResponse({"ok": True, "message": "Feedback sent successfully. Thank you!"})
    except Exception as exc:
        logger.exception("Failed to deliver feedback to Slack: %s", exc)
        return JsonResponse(
            {"detail": "Failed to deliver feedback to Slack. Please try again later."},
            status=502,
        )
