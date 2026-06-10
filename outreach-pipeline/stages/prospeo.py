"""Stage 2: find decision makers with Prospeo."""

from __future__ import annotations

import time
from typing import Any

from utils.helpers import (
    dedupe_preserve_order,
    find_first_value,
    get_env,
    get_int_env,
    join_url,
    log_error,
    normalize_domain,
    request_json,
)

STAGE = "Stage 2"
DEFAULT_BASE_URL = "https://api.prospeo.io"
DEFAULT_ENDPOINT = "/search-person"
DECISION_MAKER_KEYWORDS = (
    "ceo",
    "chief",
    "cto",
    "cfo",
    "coo",
    "vp",
    "vice president",
    "director",
    "founder",
    "president",
)
JOB_TITLE_BOOLEAN_SEARCH = (
    "(CEO OR CTO OR CFO OR COO OR Founder OR President OR VP OR "
    "'Vice President' OR Director OR Chief) AND !Intern"
)


def _headers(api_key: str) -> dict[str, str]:
    """Build Prospeo request headers."""
    return {
        "X-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _search_person_payload(domain: str, limit: int) -> dict[str, Any]:
    """Build the current Prospeo /search-person payload for one company domain."""
    return {
        "page": 1,
        "filters": {
            "company": {
                "websites": {
                    "include": [domain],
                }
            },
            "person_job_title": {
                "boolean_search": JOB_TITLE_BOOLEAN_SEARCH,
            },
            "person_seniority": {
                "include": ["C-Suite", "Vice President", "Director"],
            },
            "max_person_per_company": limit,
        },
    }


def _legacy_domain_search_payload(domain: str, limit: int) -> dict[str, Any]:
    """Build the legacy Prospeo /domain-search payload from the original spec."""
    return {"company": domain, "limit": limit}


def _payload_for_endpoint(endpoint: str, domain: str, limit: int) -> dict[str, Any]:
    """Choose the right Prospeo request payload based on configured endpoint."""
    if endpoint.rstrip("/") == "/domain-search":
        return _legacy_domain_search_payload(domain, limit)
    return _search_person_payload(domain, limit)


def _result_records(payload: dict[str, Any]) -> list[Any]:
    """Extract contact records from either current or legacy Prospeo response shapes."""
    records = payload.get("results") or payload.get("contacts") or payload.get("data") or []
    return records if isinstance(records, list) else []


def _extract_contact(record: Any, fallback_domain: str) -> dict[str, str] | None:
    """Normalize one Prospeo contact record into the pipeline contact schema."""
    person = record.get("person", record) if isinstance(record, dict) else record
    company = record.get("company", {}) if isinstance(record, dict) else {}
    name = find_first_value(person, ("full_name", "fullName", "name"))
    if not name:
        first = find_first_value(person, ("first_name", "firstName"))
        last = find_first_value(person, ("last_name", "lastName"))
        name = " ".join(part for part in (first, last) if isinstance(part, str) and part)
    title = find_first_value(person, ("job_title", "jobTitle", "title", "headline", "position"))
    linkedin_url = find_first_value(
        person,
        ("linkedin_url", "linkedinUrl", "linkedin", "linkedinProfileUrl", "profile_url"),
    )
    company_name = find_first_value(company, ("name", "company_name", "companyName")) or find_first_value(
        record, ("company_name", "companyName")
    )
    domain = find_first_value(company, ("domain", "website", "website_url", "websiteUrl")) or fallback_domain

    if not all(isinstance(value, str) and value.strip() for value in (name, title, linkedin_url)):
        return None
    if not is_decision_maker_title(title):
        return None
    normalized_domain = normalize_domain(str(domain)) or fallback_domain
    return {
        "name": str(name).strip(),
        "title": str(title).strip(),
        "linkedin_url": str(linkedin_url).strip(),
        "company": str(company_name or normalized_domain).strip(),
        "domain": normalized_domain,
    }


def is_decision_maker_title(title: str) -> bool:
    """Return true when a job title looks C-suite, VP, director, founder, or president level."""
    lower = title.lower()
    return any(keyword in lower for keyword in DECISION_MAKER_KEYWORDS)


def get_decision_makers(domains: list[str]) -> list[dict[str, str]]:
    """Given company domains, return C-suite/VP contacts that include LinkedIn URLs."""
    api_key = get_env("PROSPEO_API_KEY", required=True)
    base_url = get_env("PROSPEO_BASE_URL", DEFAULT_BASE_URL)
    endpoint = get_env("PROSPEO_ENDPOINT", DEFAULT_ENDPOINT)
    max_domains = min(get_int_env("PROSPEO_MAX_DOMAINS", 10), 10)
    contacts_per_domain = get_int_env("PROSPEO_CONTACTS_PER_DOMAIN", 5)
    url = join_url(base_url, endpoint)

    contacts: list[dict[str, str]] = []
    for domain in domains[:max_domains]:
        normalized_domain = normalize_domain(domain)
        if not normalized_domain:
            continue
        try:
            payload = request_json(
                "POST",
                url,
                stage=STAGE,
                headers=_headers(api_key),
                json_body=_payload_for_endpoint(endpoint, normalized_domain, contacts_per_domain),
                retries=3,
                backoff_seconds=(2.0, 4.0, 8.0),
            )
        except RuntimeError as exc:
            log_error(STAGE, f"Skipping {normalized_domain}: {exc}")
            time.sleep(1.1)
            continue

        domain_contacts = [
            contact
            for record in _result_records(payload)
            if (contact := _extract_contact(record, normalized_domain)) is not None
        ]
        if not domain_contacts:
            log_error(STAGE, f"No usable decision-maker contacts for {normalized_domain}")
        contacts.extend(domain_contacts)
        time.sleep(1.1)

    return dedupe_preserve_order(contacts, key=lambda item: item["linkedin_url"])
