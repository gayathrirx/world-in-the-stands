from ddgs import DDGS

WEB_QUERIES = [
    "world cup 2026 visitors USA funny experience reddit",
    "world cup 2026 fans america heartwarming moment reddit",
    "foreign fans american food culture shock world cup 2026 reddit",
    "world cup 2026 international visitors kindness USA reddit",
    "world cup 2026 fans surprised america first time reddit",
    "world cup 2026 visitors enjoying USA stadium reddit",
    "world cup 2026 visiting fans generous americans reddit",
    "world cup 2026 fans america funny cultural moment twitter",
    "world cup 2026 visitor USA experience twitter reaction",
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
