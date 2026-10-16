import logging
from collections import defaultdict
from pathlib import Path
import time
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.models import FeedbackRequest, FeedbackResponse
from app.slack import send_to_slack

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("biocore_feedback")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Biocore Feedback Service",
    description="Central feedback relay microservice and widget distributor for Biocore CRG apps",
    version="0.1.0",
)

# Setup CORS
allowed_origins: List[str] = [orig.strip() for orig in settings.allowed_origins.split(",") if orig.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# In-memory rate limiting per client IP (requests in last 60 seconds)
ip_request_timestamps: Dict[str, List[float]] = defaultdict(list)


def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    window_start = now - 60.0
    # Clean up older timestamps
    ip_request_timestamps[client_ip] = [ts for ts in ip_request_timestamps[client_ip] if ts > window_start]
    if len(ip_request_timestamps[client_ip]) >= settings.rate_limit_per_minute:
        return False
    ip_request_timestamps[client_ip].append(now)
    return True


@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "ok",
        "slack_configured": bool(settings.slack_webhook_url),
    }


@app.get("/widget.js", tags=["widget"])
async def get_widget():
    widget_file = STATIC_DIR / "widget.js"
    if not widget_file.exists():
        raise HTTPException(status_code=404, detail="Widget script not found")
    return FileResponse(
        widget_file,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=300",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.post("/api/feedback", response_model=FeedbackResponse, tags=["feedback"])
async def submit_feedback(feedback: FeedbackRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limit check
    if not check_rate_limit(client_ip):
        logger.warning("Rate limit exceeded for IP %s", client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many feedback submissions. Please wait a minute before submitting again.",
        )

    if not settings.slack_webhook_url:
        logger.error("SLACK_WEBHOOK_URL is not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Slack webhook is not configured on the server. Please contact the administrator.",
        )

    # Attach user agent if not provided
    if not feedback.user_agent:
        feedback.user_agent = request.headers.get("user-agent")

    try:
        await send_to_slack(settings.slack_webhook_url, feedback)
        logger.info("Feedback sent to Slack successfully for app '%s' from '%s'", feedback.app, feedback.name)
        return FeedbackResponse(ok=True, message="Feedback sent successfully. Thank you!")
    except Exception as exc:
        logger.exception("Failed to deliver feedback to Slack: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to deliver feedback to Slack. Please try again later.",
        )
