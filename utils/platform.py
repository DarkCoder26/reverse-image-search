"""
Robust platform detection using tldextract.
Handles public suffixes like .co.uk, .com.br correctly.
"""
import tldextract
from config.settings import PLATFORM_NAMES

# Disable network fetch at import; use bundled snapshot.
# Call tldextract.TLDExtract(..., suffix_list_urls=()) for
# fully offline behavior.
_extractor = tldextract.TLDExtract(
    suffix_list_urls=(),
    cache_dir=None,
)


def get_platform_name(url: str) -> str:
    """
    Return a human-readable platform name from a URL.

    Examples
    --------
    >>> get_platform_name("https://m.facebook.com/photo/123")
    'Facebook'
    >>> get_platform_name("https://www.bbc.co.uk/news")
    'Bbc'
    >>> get_platform_name("not-a-url")
    'Unknown'
    """
    if not url or not isinstance(url, str):
        return "Unknown"

    try:
        ext = _extractor(url)
        domain = (ext.domain or "").lower()

        if not domain:
            return "Unknown"

        if domain in PLATFORM_NAMES:
            return PLATFORM_NAMES[domain]

        return domain.capitalize()

    except Exception:
        return "Unknown"