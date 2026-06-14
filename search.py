from ddgs import DDGS

# Recent text searches (timelimit="w" = last 7 days)
TEXT_QUERIES = [
    "world cup 2026 fan USA experience reddit",
    "world cup 2026 visiting supporter america funny reddit",
    "world cup 2026 international fan USA kindness heartwarming reddit",
    "world cup 2026 tourist america food culture shock reddit",
    "world cup 2026 fan stadium USA atmosphere reddit",
    "world cup 2026 visitor america personal story twitter",
    "world cup 2026 fan USA instagram",
    "world cup 2026 visiting fan america facebook",
]

# News queries — real-time, surfaces viral/trending posts today
NEWS_QUERIES = [
    "world cup 2026 fan USA viral moment",
    "world cup 2026 international visitor america experience",
    "world cup 2026 foreign fan reaction USA",
    "world cup 2026 fan story america heartwarming funny",
    "world cup 2026 visitor USA culture shock",
    "world cup 2026 fan america stadium atmosphere",
    "world cup 2026 tourist houston dallas los angeles",
    "world cup 2026 fan USA food reaction",
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


def _text_search(query: str, max_results: int = 8) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return [
                {"title": r.get("title", ""), "body": r.get("body", ""), "url": r.get("href", ""), "source": _classify_url(r.get("href", ""))}
                for r in ddgs.text(query, max_results=max_results, timelimit="w")
            ]
    except Exception as e:
        print(f"Text search error: {e}")
        return []


def _news_search(query: str, max_results: int = 8) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return [
                {"title": r.get("title", ""), "body": r.get("body", ""), "url": r.get("url", ""), "source": _classify_url(r.get("url", ""))}
                for r in ddgs.news(query, max_results=max_results, timelimit="w")
            ]
    except Exception as e:
        print(f"News search error: {e}")
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

    for q in NEWS_QUERIES:
        _add(_news_search(q, max_results=10))

    for q in TEXT_QUERIES:
        _add(_text_search(q, max_results=8))

    print(f"Fetched {len(results)} raw results")
    return results


def fetch_match_buzz() -> list[dict]:
    seen = set()
    results = []
    for q in ["world cup 2026 match result fan reaction", "world cup 2026 goal upset fans today"]:
        for item in _news_search(q, max_results=10):
            if item["url"] not in seen:
                seen.add(item["url"])
                results.append(item)
    return results
