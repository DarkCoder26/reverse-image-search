"""
Unified orchestrator: runs enabled providers, merges,
dedupes, and ranks results.
"""
import logging
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Tuple

from models.result import AnalysisResult, SearchResult
from services import vision_service, lens_service
from config.settings import load_config

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Provider registry
# ------------------------------------------------------------------
def _provider_registry():
    cfg = load_config()
    reg = []
    if cfg.vision_enabled:
        reg.append(("Google Vision", vision_service.search))
    if cfg.lens_enabled and cfg.serpapi_key:
        reg.append(("Google Lens", lens_service.search))
    return reg


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _dedupe(results: List[SearchResult]) -> List[SearchResult]:
    """
    Collapse duplicate URLs, keeping the highest-score entry
    and merging provider info.
    """
    seen: "OrderedDict[str, SearchResult]" = OrderedDict()

    for r in results:
        key = r.url.rstrip("/")
        if key not in seen or r.score > seen[key].score:
            seen[key] = r

    return list(seen.values())


def _rank(results: List[SearchResult]) -> List[SearchResult]:
    """
    Rank by match type priority then by score descending.
    """
    priority = {
        "Full Image Match": 0,
        "Original Source": 0,
        "Partial Image Match": 1,
        "Visually Similar": 2,
        "Page with Matching Image": 3,
    }
    return sorted(
        results,
        key=lambda r: (priority.get(r.match_type.value, 9), -r.score),
    )


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def run_search(image_bytes: bytes) -> AnalysisResult:
    """
    Execute all enabled providers in parallel and return a
    merged :class:`AnalysisResult`.
    """
    providers = _provider_registry()

    if not providers:
        return AnalysisResult(
            errors=["No search providers are enabled. "
                    "Configure Vision or Lens credentials."],
        )

    all_results: List[SearchResult] = []
    labels: List[str] = []
    entities: List[str] = []
    errors: List[str] = []
    used: List[str] = []

    with ThreadPoolExecutor(max_workers=len(providers)) as pool:
        futures = {
            pool.submit(fn, image_bytes): name
            for name, fn in providers
        }
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                data = fut.result()
                used.append(name)
                all_results.extend(data.get("results", []))
                labels.extend(data.get("labels", []))
                entities.extend(data.get("entities", []))
            except Exception as exc:
                logger.exception("Provider %s failed", name)
                errors.append(f"{name}: {exc}")

    deduped = _dedupe(all_results)
    ranked = _rank(deduped)

    cfg = load_config()
    ranked = ranked[: cfg.max_results_per_provider * len(providers)]

    return AnalysisResult(
        labels=sorted(set(labels)),
        entities=sorted(set(entities)),
        results=ranked,
        providers_used=used,
        errors=errors,
    )