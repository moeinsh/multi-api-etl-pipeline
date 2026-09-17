"""HTTP client with retries + exponential backoff and a polite User-Agent."""

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

log = logging.getLogger("etl.extract")


def make_session() -> requests.Session:
    """A session that retries idempotent GETs with exponential backoff."""
    retry = Retry(
        total=config.MAX_RETRIES - 1,
        backoff_factor=config.BACKOFF_FACTOR,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": config.USER_AGENT})
    return session


def get_json(session: requests.Session, url: str, params=None, label="request"):
    """GET url, return parsed JSON. Raises RuntimeError after retries."""
    try:
        resp = session.get(url, params=params, timeout=config.HTTP_TIMEOUT)
        resp.raise_for_status()
        time.sleep(config.REQUEST_DELAY)  # polite pause between calls
        return resp.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"{label} failed after retries: {exc}") from exc
