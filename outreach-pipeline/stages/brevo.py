"""Stage 4: send personalized cold outreach emails with Brevo."""

from __future__ import annotations

import time
from typing import Any

from utils.helpers import (
    append_json_log,
    first_name,
    get_env,
    html_paragraphs,
    join_url,
    log_error,
    request_json,
    utc_now_iso,
)

STAGE = "Stage 4"
DEFAULT_BASE_URL = "https://api.brevo.com/v3"
SEND_ENDPOINT = "/smtp/email"


def _headers(api_key: str) -> dict[str, str]:
    """Build Brevo transactional email API headers."""
    return {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _email_copy(lead: dict[str, str]) -> tuple[str, str]:
    """Build the personalized subject and HTML body for one lead."""
    lead_first_name = first_name(lead.get("name", ""))
    company = lead.get("company") or lead.get("domain") or "your team"
    subject = f"Quick question, {lead_first_name}"
    body = f"""Hi {lead_first_name},

I came across {company} while researching companies doing interesting work
in the space - impressive what your team has built.

I'm Charan, a full-stack AI engineer. I've been building automation systems
that help teams eliminate manual steps in their workflows - recently shipped
a multi-agent pipeline on AWS that handles end-to-end orchestration with
zero human handoff.

Would love to explore if there's a fit. Open to a quick 15-minute call this
week?

Best,
Charan"""
    return subject, html_paragraphs(body)


def _payload_for_lead(lead: dict[str, str], sender_name: str, sender_email: str) -> dict[str, Any]:
    """Build the Brevo /smtp/email request body for one lead."""
    subject, html_content = _email_copy(lead)
    return {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": lead["email"], "name": lead.get("name", "")}],
        "subject": subject,
        "htmlContent": html_content,
    }


def send_emails(leads: list[dict[str, str]]) -> dict[str, int]:
    """Send one personalized Brevo email per verified lead and return sent/failed counts."""
    api_key = get_env("BREVO_API_KEY", required=True)
    sender_email = get_env("SENDER_EMAIL", required=True)
    sender_name = get_env("SENDER_NAME", required=True)
    url = join_url(get_env("BREVO_BASE_URL", DEFAULT_BASE_URL), SEND_ENDPOINT)
    summary = {"sent": 0, "failed": 0}

    for lead in leads:
        try:
            response = request_json(
                "POST",
                url,
                stage=STAGE,
                headers=_headers(api_key),
                json_body=_payload_for_lead(lead, sender_name, sender_email),
                retries=3,
                backoff_seconds=(2.0, 4.0, 8.0),
            )
        except RuntimeError as exc:
            summary["failed"] += 1
            log_error(STAGE, f"Failed sending to {lead.get('email', 'unknown email')}: {exc}")
            time.sleep(0.5)
            continue

        summary["sent"] += 1
        append_json_log(
            "sent_emails.json",
            {
                "timestamp": utc_now_iso(),
                "email": lead["email"],
                "name": lead.get("name", ""),
                "company": lead.get("company", ""),
                "domain": lead.get("domain", ""),
                "message_id": response.get("messageId") or response.get("message_id"),
            },
        )
        time.sleep(0.5)

    return summary
