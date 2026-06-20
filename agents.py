import anthropic
import json
import os
from search import fetch_all_stories, fetch_match_buzz

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

CATEGORY_MAP = {
    "funny": {"label": "Funny", "css": "funny"},
    "heartwarming": {"label": "Heartwarming", "css": "heartwarming"},
    "food": {"label": "Food Shock", "css": "food"},
    "culture": {"label": "Culture", "css": "culture"},
    "stadium": {"label": "Stadium", "css": "stadium"},
    "match": {"label": "Match Buzz", "css": "match"},
    "other": {"label": "Story", "css": "other"},
}

SOURCE_MAP = {
    "reddit": {"label": "Reddit", "icon": "", "css": "src-reddit"},
    "twitter": {"label": "X / Twitter", "icon": "", "css": "src-twitter"},
    "instagram": {"label": "Instagram", "icon": "", "css": "src-instagram"},
    "facebook": {"label": "Facebook", "icon": "", "css": "src-facebook"},
    "web": {"label": "Web", "icon": "", "css": "src-web"},
    "news": {"label": "Article", "icon": "", "css": "src-news"},
}


def detect_source(url: str, source: str) -> str:
    if "reddit.com" in url:
        return "reddit"
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    if "instagram.com" in url:
        return "instagram"
    if "facebook.com" in url or "fb.com" in url:
        return "facebook"
    news_domains = ["bbc", "cnn", "guardian", "espn", "goal.com", "theguardian", "nytimes", "reuters", "ap.org"]
    if any(d in url for d in news_domains):
        return "news"
    return source


def curate_and_tag(raw_items: list[dict], mode: str = "stories") -> list[dict]:
    if not raw_items:
        return []

    # Balance sources so Claude sees a mix — don't let Reddit crowd out other platforms
    from collections import defaultdict
    buckets = defaultdict(list)
    for item in raw_items:
        src = item.get("source", "web")
        buckets[src].append(item)

    balanced = []
    per_source = max(8, 40 // max(len(buckets), 1))
    for src in ["reddit", "twitter", "instagram", "facebook"]:
        balanced.extend(buckets[src][:per_source])
    # fill remaining slots with whatever's left
    seen_urls = {i["url"] for i in balanced}
    for item in raw_items:
        if len(balanced) >= 60:
            break
        if item["url"] not in seen_urls:
            balanced.append(item)
            seen_urls.add(item["url"])

    print(f"Curator input: {len(balanced)} items — " +
          ", ".join(f"{s}:{len(buckets[s])}" for s in ['reddit','twitter','instagram','facebook']))

    batch = balanced[:60]
    summaries = []
    for i, item in enumerate(batch):
        text = f"{item.get('title', '')} {item.get('body', '')}".strip()[:300]
        summaries.append(f"[{i}] url={item.get('url','')} | {text}")

    prompt = f"""You are curating social media posts about World Cup 2026 fans and visitors in the USA.

Here are {len(summaries)} raw search results from Reddit, X/Twitter, Instagram, and Facebook.

KEEP a post if it is about World Cup 2026 fans or visitors in the USA AND the URL is from reddit.com, x.com, twitter.com, instagram.com, or facebook.com.

Accept ANY of these:
- A fan sharing their personal experience visiting the USA for the World Cup
- Someone reacting to or commenting on fan experiences, culture, food, stadiums, kindness
- A funny, heartwarming, or surprising moment involving international fans in the USA
- Fan reactions to games, goals, wins, losses
- Observations about Americans hosting World Cup fans

REJECT only:
- Pure news articles with no fan voice (e.g. "FIFA announces schedule")
- Spam or unrelated content
- URLs not from the 4 social platforms listed above

Be GENEROUS — if in doubt, keep it. We want 15-20 stories.

For each KEPT post assign:
- category: funny | heartwarming | food | culture | stadium | other
- caption: one punchy sentence (max 120 chars) like a sports journalist
- country_guess: visitor's home country if inferable, else null
- flag: emoji flag if known, else "🌍"

Aim for variety across platforms and countries. Max 4 per category.

Raw results:
{chr(10).join(summaries)}

Respond with ONLY a JSON array. Keys: index, category, caption, country_guess, flag
Example: [{{"index": 0, "category": "funny", "caption": "Brazilian fan discovers a US small coffee is medically inadvisable.", "country_guess": "Brazil", "flag": "🇧🇷"}}]"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
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
        if idx < 0 or idx >= len(batch):
            continue
        item = batch[idx]  # use batch, not raw_items — idx refers to batch position
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
            "date": item.get("date", ""),
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
