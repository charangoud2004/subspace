import os
import logging
from typing import Any, List, Optional
from urllib.parse import urljoin
import requests


def dedupe_preserve_order(items: List[Any]) -> List[Any]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def find_first_value(data: dict, *keys: str) -> Optional[Any]:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def get_int_env(key: str, default: int = 0) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def join_url(base: str, path: str) -> str:
    return urljoin(base, path)


def log_error(message: str, exc: Optional[Exception] = None) -> None:
    if exc:
        logging.error(f"{message}: {str(exc)}")
    else:
        logging.error(message)


def normalize_domain(domain: str) -> str:
    domain = domain.lower().strip()
    for protocol in ["https://", "http://", "www."]:
        if domain.startswith(protocol):
            domain = domain[len(protocol):]
    domain = domain.rstrip("/")
    return domain


def request_json(url: str, method: str = "GET", headers: Optional[dict] = None, 
                 params: Optional[dict] = None, json: Optional[dict] = None,
                 timeout: int = 30) -> Optional[dict]:
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Request to {url} failed", e)
        return None
