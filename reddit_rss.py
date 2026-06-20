"""Fresh Reddit posts via RSS feeds (the JSON API is IP-blocked, but RSS works).

Searches within World Cup / soccer / US-city subreddits, sorted by newest,
so the feed always surfaces genuinely recent fan content.
"""
import time
import requests
from xml.etree import ElementTree as ET

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
_NS = {"a": "http://www.w3.org/2005/Atom"}

# Subreddits worth searching, with a query scoped to each via restrict_sr.
# (subreddit, query) — sorted by new, last month.
RSS_SOURCES = [
    ("worldcup", "USA fan experience"),
    ("worldcup", "visitor america"),
    ("soccer", "world cup usa fan"),
    ("MLS", "world cup 2026 fan"),
    ("ussoccer", "world cup fans"),
]

# Broad site-wide search as a fallback (relies on Curator to filter relevance).
SITEWIDE_QUERIES = [
    "world cup 2026 USA fan experience",
    "world cup 2026 foreign visitor america",
]


def _parse_feed(xml_text: str) -> list[dict]:
    out = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for e in root.findall("a:entry", _NS):
        link_el = e.find("a:link", _NS)
        url = link_el.get("href") if link_el is not None else ""
        # only real posts, not subreddit landing pages
        if "/comments/" not in url:
            continue
        title_el = e.find("a:title", _NS)
        author_el = e.find("a:author/a:name", _NS)
        content_el = e.find("a:content", _NS)
        title = title_el.text if title_el is not None else ""
        author = (author_el.text or "").replace("/u/", "") if author_el is not None else ""
        body = _strip_html(content_el.text) if content_el is not None and content_el.text else ""
        out.append({
            "title": title or "",
            "body": body[:400],
            "url": url,
            "source": "reddit",
            "author": author,
        })
    return out


def _strip_html(s: str) -> str:
    import re
    import html
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    # link/image posts have no selftext — RSS gives only this boilerplate
    if re.fullmatch(r"submitted by\s*/u/\S+\s*(\[link\])?\s*(\[comments\])?", s, re.IGNORECASE):
        return ""
    # strip trailing "submitted by /u/x [link] [comments]" from real bodies
    s = re.sub(r"\s*submitted by\s*/u/\S+\s*(\[link\])?\s*(\[comments\])?\s*$", "", s, flags=re.IGNORECASE)
    return s.strip()


def fetch_reddit_rss(max_per_feed: int = 8) -> list[dict]:
    sess = requests.Session()
    sess.headers.update({"User-Agent": _UA, "Accept": "application/atom+xml"})
    results = []
    seen = set()

    def _get(url: str) -> list[dict]:
        for attempt in range(2):
            try:
                r = sess.get(url, timeout=10)
                if r.status_code == 200 and r.text:
                    return _parse_feed(r.text)
                if r.status_code == 429:
                    time.sleep(3)  # backoff on rate limit
            except Exception as e:
                print(f"Reddit RSS error [{url[:50]}]: {e}")
                return []
        return []

    # subreddit-scoped searches
    for sub, q in RSS_SOURCES:
        url = (f"https://www.reddit.com/r/{sub}/search.rss"
               f"?q={q.replace(' ', '+')}&restrict_sr=1&sort=new&t=month&limit={max_per_feed}")
        for item in _get(url):
            if item["url"] not in seen:
                seen.add(item["url"])
                results.append(item)
        time.sleep(2)  # be polite to Reddit, avoid 429

    # site-wide fallback
    for q in SITEWIDE_QUERIES:
        url = (f"https://www.reddit.com/search.rss"
               f"?q={q.replace(' ', '+')}&sort=new&t=week&limit={max_per_feed}")
        for item in _get(url):
            if item["url"] not in seen:
                seen.add(item["url"])
                results.append(item)
        time.sleep(2)

    print(f"Reddit RSS: {len(results)} fresh posts")
    return results
