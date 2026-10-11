"""
Typed data models for search results.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class MatchType(str, Enum):
    EXACT = "Full Image Match"
    PARTIAL = "Partial Image Match"
    PAGE = "Page with Matching Image"
    VISUAL = "Visually Similar"
    SOURCE = "Original Source"


class Provider(str, Enum):
    VISION = "Google Vision"
    LENS = "Google Lens"


@dataclass
class SearchResult:
    """A single reverse-image-search hit."""
    url: str
    platform: str
    match_type: MatchType
    provider: Provider
    score: float = 0.0
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    page_url: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["match_type"] = self.match_type.value
        d["provider"] = self.provider.value
        return d


@dataclass
class AnalysisResult:
    """Overall analysis payload returned to the UI."""
    labels: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    safe_search: Optional[str] = None
    results: List[SearchResult] = field(default_factory=list)
    providers_used: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def total_results(self) -> int:
        return len(self.results)