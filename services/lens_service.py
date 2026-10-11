"""
SerpAPI Google Lens provider — true reverse image search.

SerpAPI requires a *publicly reachable* image URL, so we
upload the bytes to a temp host first. Here we use the
free ``0x0.st`` service; swap for S3 / GCS in production.
"""
import logging
from typing import List
import requests

from models.result import SearchResult, MatchType, Provider
from utils.platform import get_platform_name
from config.settings import load_config

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
UPLOAD_ENDPOINT = "https://0x0.st"


class LensServiceError(Exception):
    """Wraps any failure originating from the Lens provider."""



import logging
import os
from typing import List

import requests

from models.result import SearchResult, MatchType, Provider
from utils.platform import get_platform_name
from config.settings import load_config

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
UPLOAD_ENDPOINT = os.getenv("LENS_IMAGE_UPLOAD_ENDPOINT", "").strip()


class LensServiceError(Exception):
    """Wraps any failure originating from the Lens provider."""



def _upload_image(image_bytes: bytes, filename: str = "query.jpg") -> str:
    """Upload image using a configured multipart upload endpoint."""
    if not UPLOAD_ENDPOINT:
        raise LensServiceError(
            "Image upload is not configured. Set "
            "LENS_IMAGE_UPLOAD_ENDPOINT to a compatible upload API."
        )

    try:
        response = requests.post(
            UPLOAD_ENDPOINT,
            files={"file": (filename, image_bytes, "application/octet-stream")},
            timeout=30,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise LensServiceError(f"Image upload failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError:
        payload = None

    url = None

    if isinstance(payload, dict):
        url = payload.get("url")

        data = payload.get("data")
        if not url and isinstance(data, dict):
            url = data.get("url")

    if not url and isinstance(payload, str):
        url = payload.strip()

    if not url and payload is None:
        url = response.text.strip()

    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        raise LensServiceError(
            "Upload service did not return a valid image URL."
        )

    return url



def search(image_bytes: bytes) -> dict:
    """
    Run Google Lens via SerpAPI and return a normalized payload.
    """
    cfg = load_config()

    if not cfg.serpapi_key:
        raise LensServiceError(
            "SERPAPI_API_KEY is not configured."
        )

    image_url = _upload_image(image_bytes)

    params = {
        "api_key": cfg.serpapi_key,
        "engine": "google_lens",
        "url": image_url,
        "type": "all",
    }

    try:
        resp = requests.get(
            SERPAPI_ENDPOINT,
            params=params,
            timeout=cfg.request_timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        raise LensServiceError(f"SerpAPI request failed: {exc}") from exc
    except ValueError as exc:
        raise LensServiceError(
            "SerpAPI returned non-JSON response."
        ) from exc

    if "error" in payload:
        raise LensServiceError(payload["error"])

    results: List[SearchResult] = []

    # -------- exact matches --------
    for item in payload.get("exact_matches", []):
        link = item.get("link")
        if not link:
            continue
        results.append(SearchResult(
            url=link,
            platform=get_platform_name(link),
            match_type=MatchType.EXACT,
            provider=Provider.LENS,
            score=1.0,
            title=item.get("title"),
            thumbnail=item.get("thumbnail"),
            page_url=item.get("source"),
        ))

    # -------- visual matches --------
    for item in payload.get("visual_matches", []):
        link = item.get("link")
        if not link:
            continue
        results.append(SearchResult(
            url=link,
            platform=get_platform_name(link),
            match_type=MatchType.VISUAL,
            provider=Provider.LENS,
            score=0.75,
            title=item.get("title"),
            thumbnail=item.get("thumbnail"),
            page_url=item.get("source"),
        ))

    # -------- knowledge-graph entities --------
    entities = [
        kg.get("title")
        for kg in payload.get("knowledge_graph", [])
        if kg.get("title")
    ]

    return {
        "labels": [],
        "entities": entities,
        "safe_search": None,
        "results": results,
    }