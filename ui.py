SOCIAL_SOURCES = {"reddit", "twitter", "instagram", "facebook"}

PLATFORM_META = {
    "reddit": {
        "color": "#ff4500", "bg": "rgba(255,69,0,0.08)",
        "icon": """<svg width="16" height="16" viewBox="0 0 20 20" fill="#ff4500"><circle cx="10" cy="10" r="10"/><path fill="#fff" d="M16.67 10a1.46 1.46 0 0 0-2.47-1 7.12 7.12 0 0 0-3.85-1.23l.65-3.08 2.13.45a1 1 0 1 0 1-.97 1 1 0 0 0-.96.68l-2.38-.5a.16.16 0 0 0-.19.12l-.73 3.44a7.14 7.14 0 0 0-3.89 1.23 1.46 1.46 0 1 0-1.61 2.39 2.87 2.87 0 0 0 0 .44c0 2.24 2.61 4.06 5.83 4.06s5.83-1.82 5.83-4.06a2.87 2.87 0 0 0 0-.44 1.46 1.46 0 0 0 .64-1.53zm-9.4 1.06a1 1 0 1 1 1 1 1 1 0 0 1-1-1zm5.58 2.64a3.56 3.56 0 0 1-2.85.86 3.56 3.56 0 0 1-2.85-.86.19.19 0 0 1 .27-.27 3.2 3.2 0 0 0 2.58.65 3.2 3.2 0 0 0 2.58-.65.19.19 0 0 1 .27.27zm-.16-1.64a1 1 0 1 1 1-1 1 1 0 0 1-1 1z"/></svg>""",
        "label": "Reddit",
    },
    "twitter": {
        "color": "#1d9bf0", "bg": "rgba(29,155,240,0.08)",
        "icon": """<svg width="16" height="16" viewBox="0 0 24 24" fill="#1d9bf0"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622 5.912-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>""",
        "label": "X / Twitter",
    },
    "instagram": {
        "color": "#e1306c", "bg": "rgba(225,48,108,0.08)",
        "icon": """<svg width="16" height="16" viewBox="0 0 24 24" fill="url(#ig)"><defs><linearGradient id="ig" x1="0%" y1="100%" x2="100%" y2="0%"><stop offset="0%" stop-color="#f09433"/><stop offset="25%" stop-color="#e6683c"/><stop offset="50%" stop-color="#dc2743"/><stop offset="75%" stop-color="#cc2366"/><stop offset="100%" stop-color="#bc1888"/></linearGradient></defs><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>""",
        "label": "Instagram",
    },
    "facebook": {
        "color": "#1877f2", "bg": "rgba(24,119,242,0.08)",
        "icon": """<svg width="16" height="16" viewBox="0 0 24 24" fill="#1877f2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>""",
        "label": "Facebook",
    },
}


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.replace("www.", "")
        return host if host else ""
    except Exception:
        return ""


import re as _re

def _clean_title(t: str) -> str:
    return _re.sub(r'\s*[-|]\s*(Reddit|r/\w+)\s*$', '', t, flags=_re.IGNORECASE).strip()


def render_card(item: dict) -> str:
    cat = item["category"]
    url = item.get("url", "#")
    title = _clean_title(item.get("title", ""))
    body = item.get("body", "")
    caption = item.get("caption", "")
    flag = item.get("flag", "🌍")
    author = item.get("author", "")
    src_key = item.get("source_key", "web")
    pm = PLATFORM_META.get(src_key, {"color": "#888", "bg": "rgba(100,100,100,0.08)", "icon": "", "label": src_key})

    snippet = body if body else title
    if len(snippet) > 180:
        snippet = snippet[:177] + "..."

    date = item.get("date", "")
    author_line = f"u/{author}" if src_key == "reddit" and author else ("@" + author if author else "")
    # byline next to the icons: "u/name · 3d ago"
    meta_parts = [p for p in [author_line, date] if p]
    meta = " · ".join(meta_parts)

    return f"""
<a href="{url}" target="_blank" class="card-link">
<div class="card cat-{cat['css']}">
  <div class="card-top-bar"></div>
  <div class="card-inner">
    <div class="card-header">
      <span class="flag">{flag}</span>
      <span class="platform-icon">{pm['icon']}</span>
      {f'<span class="card-meta">{meta}</span>' if meta else ''}
      <span class="cat-badge badge-{cat['css']}">{cat['label']}</span>
    </div>
    {f'<p class="card-caption">{caption}</p>' if caption else ''}
    <div class="embed-preview" style="border-color:{pm['color']}20;background:{pm['bg']};">
      <p class="embed-text">{snippet}</p>
    </div>
  </div>
</div>
</a>"""


def render_feed(items: list[dict], active_filter: str = "all") -> str:
    if not items:
        return '<div class="empty-state">No stories yet — hit Refresh to find some!</div>'

    def _src(item):
        url = item.get("url", "")
        if "reddit.com" in url: return "reddit"
        if "twitter.com" in url or "x.com" in url: return "twitter"
        if "instagram.com" in url: return "instagram"
        if "facebook.com" in url or "fb.com" in url: return "facebook"
        return item.get("source_key", "web")

    seen_keys = set()
    social = []
    for i in items:
        url = i.get("url", "")
        src = _src(i)
        if src not in SOCIAL_SOURCES:
            continue
        title = i.get("title", "")
        title_key = "".join(c.lower() for c in title if c.isalnum())[:50]
        key = title_key if title_key else url
        if key not in seen_keys and url not in seen_keys:
            seen_keys.add(key)
            seen_keys.add(url)
            social.append(i)

    filtered = social if active_filter == "all" else [
        i for i in social if i["category_key"] == active_filter
    ]

    if not filtered:
        return '<div class="empty-state">No stories in this category yet.</div>'

    cards = "\n".join(render_card(i) for i in filtered)
    return f'<div class="feed">{cards}</div>'


STYLES = """
<style>
:root { --gold: #e8b84b; --card-bg: #16213e; --text: #e8e8e8; --muted: #888; }

.feed { display: flex; flex-direction: column; gap: 14px; padding: 4px 0; }

.card-link { text-decoration: none; display: block; }
.card-link:hover .card { border-color: rgba(232,184,75,0.35); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.card { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; transition: all 0.15s; }

.card-top-bar { height: 3px; }
.cat-funny .card-top-bar        { background: linear-gradient(90deg,#f093fb,#f5576c); }
.cat-heartwarming .card-top-bar { background: linear-gradient(90deg,#ff6b6b,#feca57); }
.cat-food .card-top-bar         { background: linear-gradient(90deg,#a8edea,#fed6e3); }
.cat-culture .card-top-bar      { background: linear-gradient(90deg,#4facfe,#00f2fe); }
.cat-stadium .card-top-bar      { background: linear-gradient(90deg,#43e97b,#38f9d7); }
.cat-other .card-top-bar        { background: linear-gradient(90deg,#a18cd1,#fbc2eb); }

.card-inner { padding: 14px; }

.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.flag { font-size: 22px; line-height: 1; flex-shrink: 0; }
.platform-icon { display: flex; align-items: center; flex-shrink: 0; }
.card-meta { flex: 1; font-size: 12px; color: #8a93a6; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.cat-badge { font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 20px; white-space: nowrap; text-transform: uppercase; letter-spacing: 0.5px; flex-shrink: 0; }
.badge-funny        { background: rgba(240,147,251,0.15); color: #f093fb; }
.badge-heartwarming { background: rgba(255,107,107,0.15); color: #ff9f9f; }
.badge-food         { background: rgba(168,237,234,0.15); color: #a8edea; }
.badge-culture      { background: rgba(79,172,254,0.15);  color: #4facfe; }
.badge-stadium      { background: rgba(67,233,123,0.15);  color: #43e97b; }
.badge-other        { background: rgba(161,140,209,0.15); color: #a18cd1; }

.card-caption { font-size: 14px; font-weight: 600; color: #e8e8e8; line-height: 1.45; margin-bottom: 10px; }
.embed-preview { border: 1px solid; border-radius: 12px; padding: 10px 12px; }
.embed-text { font-size: 13px; line-height: 1.5; color: #aaa; margin: 0 0 6px; }
.embed-footer { font-size: 11px; color: #666; margin-top: 2px; }

.empty-state { text-align: center; padding: 48px 20px; color: var(--muted); font-size: 15px; font-family: -apple-system, sans-serif; }
</style>
"""


def render_status(msg: str, is_loading: bool = True) -> str:
    spinner = '<div class="spin"></div>' if is_loading else "✅"
    return f"""
<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
  background:rgba(232,184,75,0.08);border:1px solid rgba(232,184,75,0.2);
  border-radius:12px;font-size:13px;color:#e8b84b;margin-bottom:10px;
  font-family:-apple-system,sans-serif;">
  <style>.spin{{width:13px;height:13px;border:2px solid rgba(232,184,75,0.3);
  border-top-color:#e8b84b;border-radius:50%;animation:sp 0.8s linear infinite;}}
  @keyframes sp{{to{{transform:rotate(360deg)}}}}</style>
  {spinner} {msg}
</div>"""
