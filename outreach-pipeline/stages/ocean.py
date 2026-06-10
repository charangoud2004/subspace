"""Stage 1: find lookalike company domains with Ocean.io."""

from __future__ import annotations

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

STAGE = "Stage 1"
DEFAULT_BASE_URL = "https://api.ocean.io"
DEFAULT_ENDPOINT = "/v3/search/companies"
DOMAIN_KEYS = (
    "domain",
    "primaryDomain",
    "website",
    "websiteUrl",
    "companyWebsite",
    "homepage",
    "url",
)


def _ocean_headers(api_key: str) -> dict[str, str]:
    """Build Ocean.io headers while supporting documented and legacy auth styles."""
    auth_header = get_env("OCEAN_AUTH_HEADER", "x-api-token")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth_header.lower() == "authorization":
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers[auth_header] = api_key
    return headers


def _ocean_payload(seed_domain: str, limit: int) -> dict[str, Any]:
    """Build the Ocean.io v3 lookalike search payload for a seed domain."""
    return {
        "size": limit,
        "fields": ["domain", "name", "rootUrl"],
        "companiesFilters": {
            "lookalikeDomains": [seed_domain],
        },
    }


def _extract_domain(company_record: Any) -> str:
    """Extract a domain from a flexible Ocean.io company response record."""
    if isinstance(company_record, str):
        return normalize_domain(company_record)
    value = find_first_value(company_record, DOMAIN_KEYS)
    if isinstance(value, str):
        return normalize_domain(value)
    return ""


def _extract_company_records(payload: dict[str, Any]) -> list[Any]:
    """Extract the list of company-like records from an Ocean.io response payload."""
    records = payload.get("companies") or payload.get("results") or payload.get("data") or []
    return records if isinstance(records, list) else []


def get_lookalike_companies(seed_domain: str) -> list[str]:
    """Given one seed domain, return 10-15 deduplicated lookalike company domains."""
    api_key = get_env("OCEAN_API_KEY", required=True)
    base_url = get_env("OCEAN_BASE_URL", DEFAULT_BASE_URL)
    endpoint = get_env("OCEAN_ENDPOINT", DEFAULT_ENDPOINT)
    limit = max(5, min(get_int_env("OCEAN_LOOKALIKE_LIMIT", 15), 15))
    normalized_seed = normalize_domain(seed_domain)
    if not normalized_seed:
        raise RuntimeError(f"Invalid seed domain: {seed_domain!r}")

    url = join_url(base_url, endpoint)
    payload = request_json(
        "POST",
        url,
        stage=STAGE,
        headers=_ocean_headers(api_key),
        json_body=_ocean_payload(normalized_seed, limit),
    )
    records = _extract_company_records(payload)
    domains = [_extract_domain(record) for record in records]
    domains = [domain for domain in domains if domain and domain != normalized_seed]
    unique_domains = dedupe_preserve_order(domains, key=lambda item: item)[:limit]
    if not unique_domains:
        message = "Ocean.io returned 0 lookalike company domains."
        log_error(STAGE, message)
        raise RuntimeError(message)
    return unique_domains
