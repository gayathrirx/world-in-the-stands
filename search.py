import re
from ddgs import DDGS
from reddit_rss import fetch_reddit_rss

# ── Reddit fallback (used when RSS is blocked, e.g. on datacenter IPs like HF) ──
REDDIT_QUERIES = [
    "world cup 2026 fan USA experience reddit",
    "world cup 2026 foreign fan america surprised reddit",
    "world cup 2026 international fan USA food culture shock reddit",
    "world cup 2026 fan stadium america atmosphere reddit",
    "world cup 2026 tourist USA kindness heartwarming reddit",
    "world cup 2026 visitor america personal story reddit",
    "world cup 2026 fans first time america reddit",
    "site:reddit.com world cup 2026 fan USA",
]

# ── X / Twitter ──
TWITTER_QUERIES = [
    "world cup 2026 fan USA experience site:x.com",
    "world cup 2026 visitor america funny site:twitter.com",
    "world cup 2026 international fan america reaction site:x.com",
    "world cup 2026 fans loving usa site:x.com",
]

# ── Instagram ──
INSTAGRAM_QUERIES = [
    "world cup 2026 fan USA experience site:instagram.com",
    "world cup 2026 visiting supporter america site:instagram.com",
    "world cup 2026 fans america moment site:instagram.com",
]

# ── Facebook ──
FACEBOOK_QUERIES = [
    "world cup 2026 fan USA story site:facebook.com",
    "world cup 2026 visitor america moment site:facebook.com",
    "world cup 2026 international fans usa site:facebook.com",
]

# ── Freebies / win-day deals ──
# These deals live mostly on brand X/Twitter accounts, so name brands + target X.
FREEBIE_QUERIES = [
    "Steak n Shake McDonalds Chipotle USA win world cup free site:x.com",
    "world cup 2026 USA win free food deal site:x.com",
    "USMNT win free fries burger taco promo site:x.com",
    "brand giveaway if USA wins world cup 2026 free site:x.com",
    "Jeep Wendys Popeyes restaurant world cup USA win free site:x.com",
    "world cup 2026 USA win deal free site:instagram.com",
    # broader brand/news catch-all (non-social deal pages)
    "free food deal when USA wins world cup 2026 restaurant",
    "world cup 2026 USA win brand promo giveaway",
]

# URLs that are NOT individual posts (profiles, search, explore, landing pages, etc.)
_JUNK_PATH = re.compile(
    r"(/search|/explore|/hashtag|/tags?/|/about|/help|/login|/i/|/watch/?$|"
    r"/(reels?|videos|photos)/?$|/groups/?$|/events/?$)",
    re.IGNORECASE,
)


def _classify_url(url: str) -> str:
    if "reddit.com" in url:
        return "reddit"
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    if "instagram.com" in url:
        return "instagram"
    if "facebook.com" in url or "fb.com" in url:
        return "facebook"
    news = ["bbc", "cnn", "guardian", "espn", "goal.com", "nytimes", "reuters",
            "ap.org", "fifa", "cbssports", "nbcsports", "houstonpublicmedia",
            "yahoo", "msn", "usatoday", "foxnews", "nbcnews", "abcnews"]
    if any(d in url for d in news):
        return "news"
    return "web"


def _is_real_post(url: str, source: str) -> bool:
    """Keep only URLs that point at an actual post, not a profile/search/landing page."""
    if _JUNK_PATH.search(url):
        return False
    if source == "reddit":
        return "/comments/" in url
    if source == "twitter":
        return "/status/" in url
    if source == "instagram":
        return "/p/" in url or "/reel/" in url
    if source == "facebook":
        return any(p in url for p in ("/posts/", "/story", "permalink", "/videos/", "/photo"))
    return True


_DATE_PREFIX = re.compile(
    r"^\s*(\d+\s+(hour|day|week|month)s?\s+ago|[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})"
    r"\s*[-·–—.]*\s*\.{0,3}\s*",
)
# DDG placeholder/empty snippets with no real content
_USELESS_BODY = re.compile(
    r"(the site owner hides the web page description|"
    r"submitted by\s*/u/\S+\s*\[link\]\s*\[comments\]|"
    r"^\s*$)",
    re.IGNORECASE,
)


def _extract_date(text: str) -> str:
    """Pull the leading date from a DDG snippet → '3d ago' / 'Jun 11'."""
    if not text:
        return ""
    m = _DATE_PREFIX.match(text)
    if not m:
        return ""
    raw = m.group(1)
    rel = re.match(r"(\d+)\s+(hour|day|week|month)s?\s+ago", raw)
    if rel:
        n, unit = rel.group(1), rel.group(2)[0]  # h/d/w/m
        return f"{n}{unit} ago"
    # absolute date like "Jun 11, 2026" → "Jun 11"
    abs_m = re.match(r"([A-Z][a-z]{2}\s+\d{1,2}),", raw)
    return abs_m.group(1) if abs_m else ""


def _clean_body(text: str) -> str:
    """Strip DuckDuckGo metadata noise from snippet bodies."""
    if not text:
        return ""
    text = _DATE_PREFIX.sub("", text)
    # "981 votes, 1.4K comments." vote/comment counters
    text = re.sub(r"\b[\d.,]+K?\s+(votes?|comments?|likes?|shares?)\b[.,]?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\.\.\.\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_useless(item: dict) -> bool:
    """Reject results with no usable content (placeholder titles/bodies)."""
    title = item.get("title", "").strip()
    body = item.get("body", "").strip()
    tl = title.lower()
    # "site owner hides the web page description" snippet never has value
    if "site owner hides the web page description" in body.lower():
        return True
    # bare "Link to instagram.com" style titles with no real headline
    if tl.endswith(("link to instagram.com", "link to facebook.com", "link to x.com", "link to twitter.com")):
        return True
    if tl.startswith(("link to ", "instagram.com", "facebook.com", "x.com")) and len(body) < 25:
        return True
    return False


def _text_search(query: str, max_results: int = 10) -> list[dict]:
    try:
        with DDGS() as ddgs:
            out = []
            for r in ddgs.text(query, max_results=max_results, region="us-en", timelimit="m"):
                url = r.get("href", "")
                src = _classify_url(url)
                raw_body = r.get("body", "")
                out.append({
                    "title": r.get("title", ""),
                    "body": _clean_body(raw_body),
                    "url": url,
                    "source": src,
                    "date": _extract_date(raw_body),
                })
            return out
    except Exception as e:
        print(f"Text search error [{query[:40]}]: {e}")
        return []


def _search_many(queries: list[str], max_results: int = 10) -> list[dict]:
    out = []
    for q in queries:
        out.extend(_text_search(q, max_results=max_results))
    return out


def fetch_all_stories() -> list[dict]:
    seen = set()
    results = []

    def _add(items, require_real_post=True):
        for item in items:
            url = item["url"]
            if not url or url in seen:
                continue
            src = item.get("source", "web")
            # drop non-post URLs for social platforms; keep reddit-from-RSS as-is
            if require_real_post and src in {"twitter", "instagram", "facebook"} and not _is_real_post(url, src):
                continue
            if _is_useless(item):
                continue
            seen.add(url)
            results.append(item)

    # 1. Reddit via RSS — genuinely fresh + relevant. Falls back to DDG if blocked (HF IP).
    reddit_items = []
    try:
        reddit_items = fetch_reddit_rss(max_per_feed=8)
    except Exception as e:
        print(f"Reddit RSS error: {e}")
    if not reddit_items:
        print("Reddit RSS empty — falling back to DuckDuckGo")
        reddit_items = [r for r in _search_many(REDDIT_QUERIES, 10) if r["source"] == "reddit"]
    _add(reddit_items, require_real_post=False)

    # 2. X / Instagram / Facebook via DuckDuckGo
    _add(_search_many(TWITTER_QUERIES, 10))
    _add(_search_many(INSTAGRAM_QUERIES, 10))
    _add(_search_many(FACEBOOK_QUERIES, 10))

    # 3. Freebies / win-day deals — tag them so the curator always keeps them
    freebie_items = _search_many(FREEBIE_QUERIES, 10)
    for it in freebie_items:
        it["freebie_hint"] = True
    _add(freebie_items)

    social = [r for r in results if r["source"] in {"reddit", "twitter", "instagram", "facebook"}]
    from collections import Counter
    by_src = Counter(r["source"] for r in social)
    print(f"Fetched {len(results)} raw, {len(social)} social — {dict(by_src)}")
    return results


def fetch_match_buzz() -> list[dict]:
    seen = set()
    results = []
    for q in ["world cup 2026 match fan reaction reddit", "world cup 2026 goal celebration reddit"]:
        for item in _text_search(q, max_results=10):
            if item["url"] not in seen:
                seen.add(item["url"])
                results.append(item)
    return results
