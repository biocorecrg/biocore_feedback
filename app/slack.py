import html
import logging
from typing import Any, Dict
import httpx
from app.models import FeedbackRequest

logger = logging.getLogger(__name__)


def build_slack_payload(feedback: FeedbackRequest) -> Dict[str, Any]:
    """Build a clean Slack Block Kit payload for user feedback."""
    app_text = feedback.app
    if feedback.page_url:
        app_text = f"<{feedback.page_url}|{feedback.app}>"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📬 New App Feedback",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*From:*\n{feedback.name}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Application:*\n{app_text}",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Message:*\n>{feedback.message.replace(chr(10), chr(10) + '>')}",
            },
        },
    ]

    if feedback.page_url:
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Submitted from: `{feedback.page_url}`",
                    }
                ],
            }
        )

    fallback_text = f"[Feedback] {feedback.app} - {feedback.name}: {feedback.message}"
    return {
        "text": fallback_text,
        "blocks": blocks,
    }


async def send_to_slack(webhook_url: str, feedback: FeedbackRequest) -> None:
    """Send payload to Slack webhook URL using httpx."""
    payload = build_slack_payload(feedback)
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(webhook_url, json=payload)
        if response.status_code != 200:
            logger.error("Slack webhook failed: %s %s", response.status_code, response.text)
            raise RuntimeError(f"Slack webhook returned status {response.status_code}: {response.text}")
