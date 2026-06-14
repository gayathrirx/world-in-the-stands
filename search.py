from ddgs import DDGS

WEB_QUERIES = [
    "world cup 2026 visiting fan USA personal experience reddit",
    "world cup 2026 foreign fan america first time surprised reddit",
    "world cup 2026 fan USA food reaction funny reddit",
    "world cup 2026 international fan american kindness heartwarming reddit",
    "world cup 2026 tourist USA culture shock observation reddit",
    "world cup 2026 fan stadium USA atmosphere experience reddit",
    "world cup 2026 visitor america personal story twitter",
    "world cup 2026 fan america funny observation twitter",
    "world cup 2026 visiting supporter USA moment instagram",
]

MATCH_QUERIES = [
    "world cup 2026 match result upset fan reaction reddit",
    "world cup 2026 goal celebration fans emotion reddit",
    "world cup 2026 loss heartbreak fan reaction reddit",
    "world cup 2026 match fan reaction twitter",
    "world cup 2026 stadium atmosphere fans experience reddit",
]


def web_search(query: str, max_results: int = 8) -> list[dict]:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href", ""),
                    "source": _classify_url(r.get("href", "")),
                })
        return results
    except Exception as e:
        print(f"Web search error: {e}")
        return []


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


def fetch_all_stories() -> list[dict]:
    results = []
    seen = set()
    for q in WEB_QUERIES:
        for item in web_search(q, max_results=8):
            url = item["url"]
            if url not in seen:
                seen.add(url)
                results.append(item)
    return results


def fetch_match_buzz() -> list[dict]:
    results = []
    seen = set()
    for q in MATCH_QUERIES:
        for item in web_search(q, max_results=8):
            url = item["url"]
            if url not in seen:
                seen.add(url)
                results.append(item)
    return results
