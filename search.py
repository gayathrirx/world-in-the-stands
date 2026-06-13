from ddgs import DDGS

WEB_QUERIES = [
    "funny foreign fans world cup USA 2026 site:twitter.com OR site:x.com",
    "world cup 2026 visitors surprised america heartwarming moment",
    "foreign soccer fans american food culture shock world cup 2026",
    "world cup 2026 fans kindness american strangers story site:reddit.com",
    "world cup 2026 visitor USA first time experience tweet",
    "soccer fans america world cup 2026 funny reaction site:reddit.com",
    "world cup 2026 international fans loving USA experience",
    "world cup fans america generous kind moment 2026",
]

MATCH_QUERIES = [
    "world cup 2026 match result fan reaction site:twitter.com OR site:x.com",
    "world cup 2026 goal celebration upset fan emotion reddit",
    "world cup 2026 match score reaction fans stadium",
    "world cup 2026 loss heartbreak fan reaction viral",
    "world cup 2026 shock result fan twitter reaction",
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
