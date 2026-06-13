import anthropic
import json
import os
from search import fetch_all_stories, fetch_match_buzz

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

CATEGORY_MAP = {
    "funny": {"label": "😂 Funny", "css": "funny"},
    "heartwarming": {"label": "❤️ Heartwarming", "css": "heartwarming"},
    "food": {"label": "🍔 Food Shock", "css": "food"},
    "culture": {"label": "😲 Culture", "css": "culture"},
    "stadium": {"label": "🏟️ Stadium", "css": "stadium"},
    "match": {"label": "🎉 Match Buzz", "css": "match"},
    "other": {"label": "🌐 Story", "css": "other"},
}

SOURCE_MAP = {
    "reddit": {"label": "Reddit", "icon": "🟠", "css": "src-reddit"},
    "web": {"label": "Web", "icon": "🔗", "css": "src-web"},
    "twitter": {"label": "Twitter/X", "icon": "🐦", "css": "src-twitter"},
    "news": {"label": "Article", "icon": "📰", "css": "src-news"},
}


def detect_source(url: str, source: str) -> str:
    if "reddit.com" in url:
        return "reddit"
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    if source == "web":
        news_domains = ["bbc", "cnn", "guardian", "espn", "goal.com", "theguardian", "nytimes", "reuters", "ap.org"]
        if any(d in url for d in news_domains):
            return "news"
    return source


def curate_and_tag(raw_items: list[dict], mode: str = "stories") -> list[dict]:
    if not raw_items:
        return []

    summaries = []
    for i, item in enumerate(raw_items[:40]):
        text = f"{item.get('title', '')} {item.get('body', '')}".strip()[:300]
        summaries.append(f"[{i}] url={item.get('url','')} | {text}")

    prompt = f"""You are curating social media posts about World Cup 2026 visitors experiencing the USA.

Here are {len(summaries)} raw search results. Your job:
1. Filter to only items that are genuinely about: real people's reactions, visitor experiences, fan emotions, funny/heartwarming moments, match reactions, or cultural observations. Remove duplicates and irrelevant results.
2. For each kept item, assign:
   - category: one of [funny, heartwarming, food, culture, stadium, match, other]
   - caption: one witty/warm sentence (max 120 chars) as if you're a clever sports journalist
   - country_guess: guess the fan's country if possible from context, else null
   - flag: emoji flag if country known, else "🌍"
   - has_direct_link: true if the URL goes directly to a tweet/reddit post, false if it's a news article or search result

Mode: {"fan stories — focus on visitor experiences, culture shock, kindness, humor" if mode == "stories" else "match buzz — focus on win/loss reactions, goals, upsets, emotional fan moments"}

Raw results:
{chr(10).join(summaries)}

Respond with ONLY a JSON array (max 20 items), each object having keys:
index, category, caption, country_guess, flag, has_direct_link

Example: [{{"index": 0, "category": "funny", "caption": "Ranch dressing claims another international victim.", "country_guess": "Japan", "flag": "🇯🇵", "has_direct_link": true}}]"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        tagged = json.loads(text)
    except Exception as e:
        print(f"Parse error: {e}")
        return []

    output = []
    for t in tagged:
        idx = t.get("index", -1)
        if idx < 0 or idx >= len(raw_items):
            continue
        item = raw_items[idx]
        src_key = detect_source(item.get("url", ""), item.get("source", "web"))
        cat_key = t.get("category", "other")
        output.append({
            "title": item.get("title", ""),
            "body": item.get("body", ""),
            "url": item.get("url", ""),
            "source_key": src_key,
            "source": SOURCE_MAP.get(src_key, SOURCE_MAP["web"]),
            "category_key": cat_key,
            "category": CATEGORY_MAP.get(cat_key, CATEGORY_MAP["other"]),
            "caption": t.get("caption", ""),
            "flag": t.get("flag", "🌍"),
            "country": t.get("country_guess") or "International",
            "has_direct_link": t.get("has_direct_link", False),
            "score": item.get("score"),
            "author": item.get("author", ""),
        })

    return output


def run_stories_pipeline(status_fn=None) -> list[dict]:
    if status_fn:
        status_fn("🔍 Scout Agent searching web and Reddit for visitor stories...")
    raw = fetch_all_stories()
    if status_fn:
        status_fn(f"📦 Found {len(raw)} raw results — Curator Agent filtering and tagging...")
    curated = curate_and_tag(raw, mode="stories")
    if status_fn:
        status_fn(f"✅ Done — {len(curated)} stories curated")
    return curated


def run_match_pipeline(status_fn=None) -> list[dict]:
    if status_fn:
        status_fn("🔍 Scout Agent searching for match reactions and buzz...")
    raw = fetch_match_buzz()
    if status_fn:
        status_fn(f"📦 Found {len(raw)} raw results — Curator Agent filtering and tagging...")
    curated = curate_and_tag(raw, mode="match")
    if status_fn:
        status_fn(f"✅ Done — {len(curated)} match stories curated")
    return curated
