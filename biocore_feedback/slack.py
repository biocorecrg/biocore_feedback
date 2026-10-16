import logging
from typing import Any, Dict
import requests

logger = logging.getLogger(__name__)


def build_slack_payload(name: str, app_name: str, message: str, page_url: str = None) -> Dict[str, Any]:
    """Build a clean Slack Block Kit payload for user feedback."""
    app_text = app_name
    if page_url:
        app_text = f"<{page_url}|{app_name}>"

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
                    "text": f"*From:*\n{name}",
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
                "text": f"*Message:*\n>{message.replace(chr(10), chr(10) + '>')}",
            },
        },
    ]

    if page_url:
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Submitted from: `{page_url}`",
                    }
                ],
            }
        )

    fallback_text = f"[Feedback] {app_name} - {name}: {message}"
    return {
        "text": fallback_text,
        "blocks": blocks,
    }


def send_to_slack_sync(webhook_url: str, name: str, app_name: str, message: str, page_url: str = None) -> None:
    """Send payload to Slack webhook URL synchronously using requests."""
    payload = build_slack_payload(name=name, app_name=app_name, message=message, page_url=page_url)
    response = requests.post(webhook_url, json=payload, timeout=10)
    if response.status_code != 200:
        logger.error("Slack webhook failed: %s %s", response.status_code, response.text)
        raise RuntimeError(f"Slack webhook returned status {response.status_code}: {response.text}")
