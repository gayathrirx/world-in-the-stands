from ddgs import DDGS

# Reddit — broad, no time limit so we get enough results
REDDIT_QUERIES = [
    "world cup 2026 visiting fan USA experience reddit",
    "world cup 2026 foreign fan america surprised funny reddit",
    "world cup 2026 international fan USA food culture shock reddit",
    "world cup 2026 fan stadium america atmosphere reddit",
    "world cup 2026 tourist USA kindness heartwarming reddit",
    "world cup 2026 visitor america personal story reddit",
    "world cup 2026 fan USA first time america reddit",
    "site:reddit.com world cup 2026 fan USA experience",
]

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

    all_queries = REDDIT_QUERIES + TWITTER_QUERIES + INSTAGRAM_QUERIES + FACEBOOK_QUERIES
    for q in all_queries:
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
