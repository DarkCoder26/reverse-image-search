# 🔎 Reverse Image Search

A production-ready **reverse image search** application built with **Streamlit** and **Python**. Upload an image, and the app analyses its visual content and finds the webpages and platforms where that image appears — returning **direct links** and **platform names**.

Supports two search engines out of the box:

- **Google Cloud Vision** — Web Detection API (built-in, no extra cost beyond Vision billing)
- **SerpAPI Google Lens** — true reverse image search (exact uploads)

---

## 📖 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the App](#-running-the-app)
- [Environment Variables](#-environment-variables)
- [How It Works](#-how-it-works)
- [Providers](#-providers)
- [Platform Detection](#-platform-detection)
- [Rate Limiting](#-rate-limiting)
- [Caching](#-caching)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Security Notes](#-security-notes)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Reverse image search** | Find where an image appears across the web |
| 🌐 **Platform detection** | Automatically identifies Facebook, Instagram, Reddit, Pinterest, and 40+ more |
| 🎯 **Match scoring** | Ranks results by *full match* / *partial match* / *visually similar* |
| 🧠 **Image analysis** | Shows best-guess labels and related entities detected by Vision AI |
| ⚡ **Multi-provider** | Runs Google Vision and Google Lens in parallel |
| 🛡️ **Rate limiting** | Per-session quota to protect API quotas |
| 💾 **Response caching** | 5-minute cache prevents duplicate API calls |
| ✅ **Input validation** | Format sniffing, size limits, MIME checks |
| 📊 **Professional UI** | Grouped results, thumbnails, scores, provider attribution |
| 🧩 **Modular design** | Services / models / utils / components — easy to extend |
| 📝 **Structured logging** | Observability out of the box |
| 🔒 **Secrets management** | Uses Streamlit secrets + environment fallback |

---

## 🎬 Demo

```
┌────────────────────────────────────────────┐
│  🔎 Reverse Image Search                   │
├────────────────────────────────────────────┤
│  Choose an image: [ Browse… ]              │
│                                            │
│  ┌──────────┐                              │
│  │  🖼️      │   File: photo.jpg            │
│  │  Preview │   Size: 245.3 KB            │
│  └──────────┘   Type: image/jpeg           │
│                                            │
│  [ 🔍 Search Image ]                       │
├────────────────────────────────────────────┤
│  🧠 Image Analysis                         │
│  Best-guess labels: Person, Sky, Mountain  │
│                                            │
│  🌐 Found 12 matches via Google Vision     │
│                                            │
│  🎯 Full Image Match (3)                   │
│  ┌──────────────────────────────────────┐  │
│  │ 🖼️  Facebook · Google Vision         │  │
│  │    https://facebook.com/photo/...    │  │
│  │    Score: 1.00                       │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │  Streamlit UI   │
                    │    (app.py)     │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
      ┌───────────┐   ┌────────────┐   ┌──────────┐
      │ Validator │   │  Rate      │   │  Cache   │
      │           │   │  Limiter   │   │          │
      └─────┬─────┘   └─────┬──────┘   └────┬─────┘
            └───────────────┼───────────────┘
                            ▼
                 ┌─────────────────────┐
                 │   Search Engine     │
                 │  (orchestrator)     │
                 └──────────┬──────────┘
                            │  parallel
              ┌─────────────┴─────────────┐
              ▼                           ▼
      ┌───────────────┐           ┌────────────────┐
      │ Vision Service│           │  Lens Service  │
      │  (Google)     │           │  (SerpAPI)     │
      └───────┬───────┘           └────────┬───────┘
              │                            │
              └──────────┬─────────────────┘
                         ▼
                 ┌───────────────┐
                 │  Dedup/Rank   │
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │  Results View │
                 └───────────────┘
```

---

## 📂 Project Structure

```
reverse-image-search/
├── app.py                          # Streamlit entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── credentials.json                # GCP service account (DO NOT COMMIT)
│
├── .streamlit/
│   └── secrets.toml                # Secrets (DO NOT COMMIT)
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # Config + constants
│
├── models/
│   ├── __init__.py
│   └── result.py                   # Data models (dataclasses)
│
├── services/
│   ├── __init__.py
│   ├── vision_service.py           # Google Vision provider
│   ├── lens_service.py             # SerpAPI Google Lens provider
│   └── search_engine.py            # Orchestrator
│
├── utils/
│   ├── __init__.py
│   ├── platform.py                 # tldextract-based detection
│   ├── validators.py               # Input validation
│   └── rate_limiter.py             # Session-based rate limiting
│
└── components/
    ├── __init__.py
    └── results_view.py             # Results rendering
```

---

## 📋 Prerequisites

- **Python 3.10+**
- **Google Cloud account** (for Vision API)
- **SerpAPI account** *(optional, for true reverse image search)*
- **pip** and **virtualenv** (recommended)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/reverse-image-search.git
cd reverse-image-search
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Google Cloud Vision

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the **Cloud Vision API**:
   - Navigate to *APIs & Services → Library*
   - Search for **Cloud Vision API** → **Enable**
4. Create a **service account**:
   - *IAM & Admin → Service Accounts → Create Service Account*
   - Give it the role **Cloud Vision AI User** (or `roles/vision.user`)
5. Create a JSON key:
   - Click the service account → *Keys* → *Add Key* → *Create new key* → **JSON**
6. Download the JSON file and save it in the project root as `credentials.json`

> ⚠️ **Never commit `credentials.json` to version control.** It's already listed in `.gitignore`.

### 5. Set up SerpAPI *(optional)*

1. Sign up at [serpapi.com](https://serpapi.com/)
2. Copy your API key from the dashboard
3. Add it to `.streamlit/secrets.toml` (see below)

---

## ⚙️ Configuration

### Create `.streamlit/secrets.toml`

```toml
# ------------------------------------------------------------------
# Google Vision
# ------------------------------------------------------------------
VISION_ENABLED = "true"
CREDENTIALS_FILE = "credentials.json"

# ------------------------------------------------------------------
# SerpAPI Google Lens (optional — true reverse search)
# ------------------------------------------------------------------
LENS_ENABLED = "false"
SERPAPI_API_KEY = "your_serpapi_key_here"

# ------------------------------------------------------------------
# Tuning
# ------------------------------------------------------------------
MAX_RESULTS = "50"
REQUEST_TIMEOUT = "30"
CACHE_TTL = "300"
RATE_LIMIT = "20"
RATE_WINDOW = "3600"
```

> 💡 `secrets.toml` overrides environment variables, which override defaults.

---

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will be available at **http://localhost:8501**.

### First-run checklist

- [ ] `credentials.json` exists in the project root
- [ ] Vision API is enabled in GCP
- [ ] `.streamlit/secrets.toml` is present
- [ ] Service account has `roles/vision.user`

---

## 🔧 Environment Variables

If you prefer env vars over `secrets.toml`:

| Variable | Default | Description |
|---|---|---|
| `VISION_ENABLED` | `true` | Enable Google Vision provider |
| `CREDENTIALS_FILE` | `credentials.json` | Path to GCP service account JSON |
| `LENS_ENABLED` | `false` | Enable SerpAPI Google Lens provider |
| `SERPAPI_API_KEY` | — | Your SerpAPI key |
| `MAX_RESULTS` | `50` | Max results per provider |
| `REQUEST_TIMEOUT` | `30` | HTTP timeout in seconds |
| `CACHE_TTL` | `300` | Search cache TTL in seconds |
| `RATE_LIMIT` | `20` | Max searches per session per window |
| `RATE_WINDOW` | `3600` | Rate-limit window in seconds |

Example:

```bash
export VISION_ENABLED=true
export SERPAPI_API_KEY=abc123...
export RATE_LIMIT=10
streamlit run app.py
```

---

## 🧠 How It Works

1. **Upload** — user selects an image (`jpg`, `jpeg`, `png`, `webp`, ≤ 10 MB)
2. **Validate** — file is sniffed for real format, size checked, MIME verified
3. **Rate limit** — session quota is checked before hitting any API
4. **Cache lookup** — identical image bytes within 5 min return instantly
5. **Provider fan-out** — enabled providers are called in parallel
6. **Merge + dedupe** — results from all providers are unioned, duplicates removed
7. **Rank** — sorted by match-type priority, then by score
8. **Render** — grouped by match type; each result shows platform, link, score

### Match types

| Type | Meaning | Score |
|---|---|---|
| 🎯 **Full Image Match** | Exact copy found | 1.00 |
| ✂️ **Partial Image Match** | Cropped / edited version | 0.70 |
| 👁️ **Visually Similar** | Same content, different file | 0.40–0.75 |
| 📄 **Page with Matching Image** | Page contains the image | 0.30+ |

---

## 🔌 Providers

### Google Vision (default)

- **Cost:** ~$3.50 per 1,000 web-detection requests (after free tier)
- **Coverage:** Approximate — finds pages containing similar images
- **Best for:** Free-tier exploration, broad coverage
- **Docs:** https://cloud.google.com/vision/docs/detecting-web

### Google Lens via SerpAPI (recommended for accuracy)

- **Cost:** ~$0.01–0.03 per query (SerpAPI plan dependent)
- **Coverage:** True reverse image search — exact uploads + visual matches
- **Best for:** Production use, accurate results
- **Docs:** https://serpapi.com/google-lens-api

> **Enable Lens** by setting `LENS_ENABLED = "true"` and `SERPAPI_API_KEY` in `secrets.toml`.

---

## 🌐 Platform Detection

Platform names are resolved using [`tldextract`](https://github.com/john-kurkowski/tldextract), which correctly handles public suffixes such as `.co.uk`, `.com.br`, and `.co.jp`.

```python
from utils.platform import get_platform_name

get_platform_name("https://m.facebook.com/photo/123")  # "Facebook"
get_platform_name("https://www.bbc.co.uk/news")        # "Bbc"
get_platform_name("https://old.reddit.com/r/pics")     # "Reddit"
```

### Supported platforms (40+)

Facebook, Instagram, Pinterest, Reddit, X (Twitter), YouTube, TikTok, LinkedIn, GitHub, Medium, Flickr, Tumblr, Imgur, 9GAG, DeviantArt, ArtStation, Behance, Dribbble, Unsplash, Pexels, Pixabay, Shutterstock, Getty Images, Alamy, iStock, Etsy, eBay, Amazon, AliExpress, Walmart, Wikipedia, Wikimedia, Blogspot, WordPress, VK, Weibo, QQ, Baidu.

*(See `config/settings.py` → `PLATFORM_NAMES` to add more.)*

---

## 🛡️ Rate Limiting

Each browser session is limited to **20 searches per hour** (configurable).

- Backed by `st.session_state` — resets when the browser session ends
- Sidebar displays remaining quota in real time
- **For multi-instance deployments**, replace `utils/rate_limiter.py` with a Redis-backed implementation

```python
# Example Redis replacement
import redis
r = redis.Redis(host="localhost", port=6379)
r.incr(f"rl:{session_id}")
r.expire(f"rl:{session_id}", 3600)
```

---

## 💾 Caching

Search results are cached for **5 minutes** using `@st.cache_data`.

- Keyed by image byte hash — the same image never hits the API twice in the window
- Reduces cost and improves perceived speed
- Adjust with `CACHE_TTL` in `secrets.toml`

---

## ☁️ Deployment

### Streamlit Community Cloud

1. Push your code to a **public or private** GitHub repo
2. **Do not push** `credentials.json` or `secrets.toml`
3. In [share.streamlit.io](https://share.streamlit.io), create a new app
4. Under *Advanced settings → Secrets*, paste the contents of your `secrets.toml`
5. For `credentials.json`, base64-encode it and store it as a secret, then decode at startup:

   ```bash
   base64 -i credentials.json | pbcopy   # macOS
   base64 -w 0 credentials.json          # Linux
   ```

   Then in `services/vision_service.py`:
   ```python
   import base64, json, os
   from google.oauth2 import service_account

   def _build_client(_cfg):
       info = json.loads(base64.b64decode(st.secrets["GCP_CREDENTIALS_B64"]))
       creds = service_account.Credentials.from_service_account_info(info)
       return vision.ImageAnnotatorClient(credentials=creds)
   ```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libmagic1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0"]
```

```bash
docker build -t reverse-image-search .
docker run -p 8501:8501 \
    -v $(pwd)/credentials.json:/app/credentials.json:ro \
    -v $(pwd)/.streamlit:/app/.streamlit:ro \
    reverse-image-search
```

### Reverse proxy (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name search.example.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Credentials file 'credentials.json' not found` | File missing | Place the service account JSON in the project root |
| `Vision API call failed: 403 PERMISSION_DENIED` | API not enabled, or SA lacks role | Enable Cloud Vision API; grant `roles/vision.user` |
| `No search providers are enabled` | All providers disabled | Set `VISION_ENABLED=true` or `LENS_ENABLED=true` + key |
| `Rate limit reached` | Session quota hit | Wait, or raise `RATE_LIMIT` in secrets |
| `Unsupported image format` | Corrupt/odd file | Re-save as JPEG or PNG |
| `No matching webpages were found` | Vision's coverage is approximate | Enable Lens provider for accuracy |
| `Image upload failed` | Temporary host (`0x0.st`) down | Swap for S3/GCS in `lens_service.py` |

### Enable debug logging

```bash
export PYTHONUNBUFFERED=1
streamlit run app.py --logger.level=debug
```

---

## 🔒 Security Notes

- **Never commit** `credentials.json` or `.streamlit/secrets.toml`
- Rotate service-account keys on a regular schedule
- For public deployments, put the app behind authentication:
  - Use `streamlit-authenticator`, or
  - Put it behind Cloudflare Access / OAuth proxy
- The SerpAPI Lens provider uploads images to a **temporary public host** (`0x0.st`). For production, **replace this** with your own S3/GCS bucket using short-lived signed URLs.
- Consider enabling **Vision SafeSearch** (`safe_search` field is exposed in `AnalysisResult`) to filter adult content.

---

## 🧪 Testing (Coming Soon)

```bash
pytest tests/
```

Suggested test layout:

```
tests/
├── test_platform.py         # get_platform_name
├── test_validators.py       # validate_image
├── test_rate_limiter.py     # quota behaviour
└── test_search_engine.py    # dedup + rank logic
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please follow [PEP 8](https://peps.python.org/pep-0008/) and include type hints.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) — UI framework
- [Google Cloud Vision](https://cloud.google.com/vision) — Web Detection
- [SerpAPI](https://serpapi.com/) — Google Lens API
- [tldextract](https://github.com/john-kurkowski/tldextract) — accurate domain parsing

---

## 📞 Support

- 🐛 **Bug reports:** [Open an issue](https://github.com/your-username/reverse-image-search/issues)
- 💡 **Feature requests:** [Start a discussion](https://github.com/your-username/reverse-image-search/discussions)
- 📧 **Email:** you@example.com

---

<p align="center">
  <strong>⭐ If this project helped you, please give it a star!</strong>
</p>