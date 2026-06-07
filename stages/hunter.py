"""Stage 3: resolve contacts to verified work emails with Hunter.io."""

from __future__ import annotations

import time

from utils.helpers import (
    dedupe_preserve_order,
    find_first_value,
    get_env,
    join_url,
    log_error,
    request_json,
)

STAGE = "Stage 3"
DEFAULT_BASE_URL = "https://api.hunter.io/v2"
EMAIL_FINDER_ENDPOINT = "/email-finder"


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(None, 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], ""
    return "", ""


def _resolve_with_hunter(contact: dict[str, str], api_key: str, base_url: str) -> str:
    first, last = split_name(contact.get("name", ""))
    if not first or not last:
        log_error(STAGE, f"Skipping {contact.get('name', 'unknown contact')}: Hunter needs first and last name")
        return ""

    payload = request_json(
        "GET",
        join_url(base_url, EMAIL_FINDER_ENDPOINT),
        stage=STAGE,
        params={
            "domain": contact["domain"],
            "first_name": first,
            "last_name": last,
            "api_key": api_key,
        },
        retries=3,
        backoff_seconds=(2.0, 4.0, 8.0),
    )
    data = payload.get("data", payload)
    email = find_first_value(data, ("email", "value"))
    return str(email).strip() if isinstance(email, str) and "@" in email else ""


def resolve_emails(contacts: list[dict[str, str]]) -> list[dict[str, str]]:
    api_key = get_env("HUNTER_API_KEY", required=True)
    base_url = get_env("HUNTER_BASE_URL", DEFAULT_BASE_URL)
    unique_contacts = dedupe_preserve_order(contacts, key=lambda item: item.get("linkedin_url", ""))

    leads: list[dict[str, str]] = []
    for contact in unique_contacts:
        try:
            email = _resolve_with_hunter(contact, api_key, base_url)
        except RuntimeError as exc:
            log_error(STAGE, f"Skipping {contact.get('name', 'unknown contact')}: {exc}")
            continue
        if not email:
            log_error(STAGE, f"No email resolved for {contact.get('name', 'unknown contact')}")
            continue
        lead = dict(contact)
        lead["email"] = email
        leads.append(lead)
        time.sleep(1.0)

    return dedupe_preserve_order(leads, key=lambda item: item["email"])
