"""Search clients (Tavily web, HN Algolia, GitHub) + research() orchestration."""
import datetime
import logging
import time
from urllib.parse import urlparse

import httpx
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

MAX_ITEMS = 40
SNIPPET_LEN = 600


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _truncate(text: str | None, limit: int = SNIPPET_LEN) -> str:
    return (text or "")[:limit]


def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    """Search recent web content via Tavily. Returns raw result dicts."""
    from tavily import TavilyClient

    api_key = settings.TAVILY_API_KEY
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")
    client = TavilyClient(api_key=api_key)
    # Restrict to roughly last 30 days where supported.
    resp = client.search(query, max_results=max_results, time_range="month", include_answer=False)
    if isinstance(resp, dict):
        return resp.get("results", [])
    return []


def hn_search(topic: str, limit: int = 10) -> list[dict]:
    """Search HN stories from the last ~30 days via Algolia API."""
    ts_30d_ago = int(time.time()) - 30 * 24 * 3600
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "query": topic,
        "tags": "story",
        "numericFilters": f"created_at_i>{ts_30d_ago}",
    }
    with httpx.Client(timeout=20.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        hits = r.json().get("hits", [])
    return hits[:limit]


def github_search(topic: str, limit: int = 10) -> list[dict]:
    """Search repos created in the last ~30 days, sorted by stars."""
    date_30d_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"{topic} created:>{date_30d_ago}",
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }
    headers = {"Accept": "application/vnd.github+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    with httpx.Client(timeout=20.0) as client:
        r = client.get(url, params=params, headers=headers)
        r.raise_for_status()
        items = r.json().get("items", [])
    return items[:limit]


def research(run, queries: list[str]):
    """Run all sources, save Item rows on run, return saved Item list. Network only."""
    from research.models import Item

    seen_urls: set[str] = set()
    pending: list[Item] = []

    def add(source: str, url: str, title: str, snippet: str, published_at=None, meta=None):
        if not url or url in seen_urls:
            return
        if len(seen_urls) >= MAX_ITEMS:
            return
        seen_urls.add(url)
        pending.append(
            Item(
                run=run,
                source=source,
                url=url[:1000],
                title=(title or "Untitled")[:500],
                snippet=_truncate(snippet),
                domain=_domain(url)[:200],
                published_at=published_at,
                meta=meta or {},
            )
        )

    # Tavily web
    for q in queries:
        try:
            for res in tavily_search(q):
                url = res.get("url", "")
                add(
                    "web",
                    url,
                    res.get("title", ""),
                    res.get("content", "") or res.get("snippet", ""),
                    published_at=None,
                    meta={},
                )
                if len(seen_urls) >= MAX_ITEMS:
                    break
        except Exception:
            logger.exception("Tavily search failed for query: %s", q)
        if len(seen_urls) >= MAX_ITEMS:
            break

    # Hacker News
    try:
        for hit in hn_search(run.topic):
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            created = hit.get("created_at")
            published_at = None
            if created:
                try:
                    published_at = timezone.datetime.fromisoformat(created.replace("Z", "+00:00"))
                except Exception:
                    published_at = None
            add(
                "hn",
                url,
                hit.get("title", ""),
                f"{hit.get('title', '')}",
                published_at=published_at,
                meta={"points": hit.get("points")},
            )
    except Exception:
        logger.exception("HN search failed")

    # GitHub
    try:
        for repo in github_search(run.topic):
            add(
                "github",
                repo.get("html_url", ""),
                repo.get("full_name", ""),
                repo.get("description", ""),
                published_at=None,
                meta={"stars": repo.get("stargazers_count")},
            )
    except Exception:
        logger.exception("GitHub search failed")

    if not pending:
        raise RuntimeError("No items found from any source")

    saved: list[Item] = []
    for item in pending[:MAX_ITEMS]:
        obj, _ = Item.objects.update_or_create(
            run=item.run,
            url=item.url,
            defaults={
                "source": item.source,
                "title": item.title,
                "snippet": item.snippet,
                "domain": item.domain,
                "published_at": item.published_at,
                "meta": item.meta,
            },
        )
        saved.append(obj)
    return saved
