"""
Google Cloud Vision Web Detection provider.
"""
import logging
from typing import List
from google.cloud import vision
from google.oauth2 import service_account

from models.result import SearchResult, MatchType, Provider
from utils.platform import get_platform_name
from config.settings import load_config

logger = logging.getLogger(__name__)


class VisionServiceError(Exception):
    """Wraps any failure originating from the Vision provider."""


def _build_client(credentials_file: str) -> vision.ImageAnnotatorClient:
    """Create an authenticated Vision client."""
    try:
        credentials = (
            service_account.Credentials
            .from_service_account_file(credentials_file)
        )
    except FileNotFoundError as exc:
        raise VisionServiceError(
            f"Credentials file '{credentials_file}' not found."
        ) from exc
    except Exception as exc:
        raise VisionServiceError(
            f"Failed to load credentials: {exc}"
        ) from exc

    return vision.ImageAnnotatorClient(credentials=credentials)


def search(image_bytes: bytes) -> dict:
    """
    Run Web Detection and return a normalized payload:

    {
        "labels": [...],
        "entities": [...],
        "safe_search": "VERY_UNLIKELY" | ...,
        "results": [SearchResult, ...],
    }
    """
    cfg = load_config()
    client = _build_client(cfg.credentials_file)

    image = vision.Image(content=image_bytes)

    try:
        response = client.web_detection(image=image)
    except Exception as exc:
        raise VisionServiceError(f"Vision API call failed: {exc}") from exc

    if response.error.message:
        raise VisionServiceError(response.error.message)

    wd = response.web_detection

    # ---------------- labels / entities ----------------
    labels = [lbl.label for lbl in wd.best_guess_labels if lbl.label]
    entities = [
        ent.description for ent in wd.web_entities
        if ent.description and ent.score >= 0.5
    ]

    safe_search = None
    try:
        safe_search = vision.AnnotateImageResponse.to_dict(
            response
        ).get("safe_search_annotation", {}).get(
            "adult", {}
        ).get("likelihood")
    except Exception:
        pass

    # ---------------- matches ----------------
    results: List[SearchResult] = []

    # Exact matches — highest confidence
    for m in wd.full_matching_images:
        if not m.url:
            continue
        results.append(SearchResult(
            url=m.url,
            platform=get_platform_name(m.url),
            match_type=MatchType.EXACT,
            provider=Provider.VISION,
            score=1.0,
        ))

    # Partial matches
    for m in wd.partial_matching_images:
        if not m.url:
            continue
        results.append(SearchResult(
            url=m.url,
            platform=get_platform_name(m.url),
            match_type=MatchType.PARTIAL,
            provider=Provider.VISION,
            score=0.7,
        ))

    # Pages containing matching images
    for page in wd.pages_with_matching_images:
        if not page.url:
            continue
        page_score = getattr(page, "page_match", None) or 0.3
        results.append(SearchResult(
            url=page.url,
            platform=get_platform_name(page.url),
            match_type=MatchType.PAGE,
            provider=Provider.VISION,
            score=float(page_score),
            title=getattr(page, "title", None),
        ))

    # Visually similar images
    for m in wd.visually_similar_images:
        if not m.url:
            continue
        results.append(SearchResult(
            url=m.url,
            platform=get_platform_name(m.url),
            match_type=MatchType.VISUAL,
            provider=Provider.VISION,
            score=0.4,
        ))

    return {
        "labels": labels,
        "entities": entities,
        "safe_search": safe_search,
        "results": results,
    }