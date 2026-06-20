from ddgs import DDGS
from reddit_rss import fetch_reddit_rss

# X / Twitter
TWITTER_QUERIES = [
    "world cup 2026 fan USA experience site:x.com",
    "world cup 2026 visitor america funny site:twitter.com",
    "world cup 2026 international fan america reaction twitter",
]

# Instagram
INSTAGRAM_QUERIES = [
    "world cup 2026 fan USA experience site:instagram.com",
    "world cup 2026 visiting supporter america instagram",
]

# Facebook
FACEBOOK_QUERIES = [
    "world cup 2026 fan USA story site:facebook.com",
    "world cup 2026 visitor america moment facebook",
]


def _classify_url(url: str) -> str:
    if "reddit.com" in url:
        return "reddit"
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    if "instagram.com" in url:
        return "instagram"
    if "facebook.com" in url or "fb.com" in url:
        return "facebook"
    news = ["bbc", "cnn", "guardian", "espn", "goal.com", "nytimes", "reuters", "ap.org", "fifa", "cbssports", "nbcsports"]
    if any(d in url for d in news):
        return "news"
    return "web"


def _text_search(query: str, max_results: int = 10) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return [
                {"title": r.get("title", ""), "body": r.get("body", ""), "url": r.get("href", ""), "source": _classify_url(r.get("href", ""))}
                for r in ddgs.text(query, max_results=max_results)
            ]
    except Exception as e:
        print(f"Text search error [{query[:40]}]: {e}")
        return []


def fetch_all_stories() -> list[dict]:
    seen = set()
    results = []

    def _add(items):
        for item in items:
            url = item["url"]
            if url and url not in seen:
                seen.add(url)
                results.append(item)

    # 1. Reddit via RSS — genuinely fresh + relevant posts
    try:
        _add(fetch_reddit_rss(max_per_feed=8))
    except Exception as e:
        print(f"Reddit RSS failed, falling back to DDG: {e}")
        _add(_text_search("world cup 2026 fan USA experience reddit", max_results=10))

    # 2. X / Instagram / Facebook via DuckDuckGo (no free real-time API exists)
    for q in TWITTER_QUERIES + INSTAGRAM_QUERIES + FACEBOOK_QUERIES:
        _add(_text_search(q, max_results=10))

    social = [r for r in results if r["source"] in {"reddit", "twitter", "instagram", "facebook"}]
    print(f"Fetched {len(results)} raw results, {len(social)} social")
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
