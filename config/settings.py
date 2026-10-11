"""
Central configuration for the reverse image search application.
"""
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# Supported image formats
# ------------------------------------------------------------------
ALLOWED_MIME_TYPES: List[str] = [
    "image/jpeg",
    "image/png",
    "image/webp",
]

ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]

MAX_IMAGE_SIZE_MB: int = 10
MAX_IMAGE_SIZE_BYTES: int = MAX_IMAGE_SIZE_MB * 1024 * 1024

# ------------------------------------------------------------------
# Provider settings
# ------------------------------------------------------------------
@dataclass
class ProviderConfig:
    """Configuration for a single search provider."""
    name: str
    enabled: bool = True
    weight: float = 1.0          # used for cross-provider ranking


@dataclass
class AppConfig:
    """Top-level application configuration."""
    vision_enabled: bool = True
    lens_enabled: bool = False
    credentials_file: str = "credentials.json"
    serpapi_key: str = ""
    max_results_per_provider: int = 50
    request_timeout: int = 30
    cache_ttl: int = 300         # seconds
    rate_limit_per_session: int = 20
    rate_limit_window: int = 3600  # seconds


def load_config() -> AppConfig:
    """
    Load configuration from Streamlit secrets, falling back
    to environment variables, then defaults.
    """
    try:
        import streamlit as st
        secrets = st.secrets if hasattr(st, "secrets") else {}
    except Exception:
        secrets = {}

    def _get(key: str, default=""):
        return secrets.get(key, os.getenv(key, default))

    return AppConfig(
        vision_enabled=str(_get("VISION_ENABLED", "true")).lower() == "true",
        lens_enabled=str(_get("LENS_ENABLED", "false")).lower() == "true",
        credentials_file=_get("CREDENTIALS_FILE", "credentials.json"),
        serpapi_key=_get("SERPAPI_API_KEY", ""),
        max_results_per_provider=int(_get("MAX_RESULTS", "50")),
        request_timeout=int(_get("REQUEST_TIMEOUT", "30")),
        cache_ttl=int(_get("CACHE_TTL", "300")),
        rate_limit_per_session=int(_get("RATE_LIMIT", "20")),
        rate_limit_window=int(_get("RATE_WINDOW", "3600")),
    )


# ------------------------------------------------------------------
# Platform name map (domain -> display name)
# ------------------------------------------------------------------
PLATFORM_NAMES = {
    "facebook": "Facebook",
    "instagram": "Instagram",
    "pinterest": "Pinterest",
    "reddit": "Reddit",
    "x": "X (Twitter)",
    "twitter": "Twitter",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "linkedin": "LinkedIn",
    "github": "GitHub",
    "medium": "Medium",
    "flickr": "Flickr",
    "tumblr": "Tumblr",
    "imgur": "Imgur",
    "9gag": "9GAG",
    "deviantart": "DeviantArt",
    "artstation": "ArtStation",
    "behance": "Behance",
    "dribbble": "Dribbble",
    "unsplash": "Unsplash",
    "pexels": "Pexels",
    "pixabay": "Pixabay",
    "shutterstock": "Shutterstock",
    "gettyimages": "Getty Images",
    "alamy": "Alamy",
    "istockphoto": "iStock",
    "etsy": "Etsy",
    "ebay": "eBay",
    "amazon": "Amazon",
    "aliexpress": "AliExpress",
    "walmart": "Walmart",
    "wikipedia": "Wikipedia",
    "wikimedia": "Wikimedia",
    "blogspot": "Blogspot",
    "wordpress": "WordPress",
    "tumblr": "Tumblr",
    "vk": "VK",
    "weibo": "Weibo",
    "qq": "QQ",
    "baidu": "Baidu",
}