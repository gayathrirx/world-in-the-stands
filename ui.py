SOCIAL_SOURCES = {"reddit", "twitter", "instagram", "facebook"}


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.replace("www.", "")
        return host if host else url[:40]
    except Exception:
        return ""


def render_card(item: dict) -> str:
    cat = item["category"]
    src = item["source"]
    url = item.get("url", "#")
    title = item.get("title", "")
    body = item.get("body", "")
    caption = item.get("caption", "")
    flag = item.get("flag", "🌍")
    country = item.get("country", "International")
    author = item.get("author", "")
    src_key = item.get("source_key", "web")

    display_text = title if title else body
    if len(display_text) > 280:
        display_text = display_text[:277] + "..."

    score = item.get("score")
    score_html = f'<span class="reaction">⬆️ {score}</span>' if score else ""
    author_html = f'<span class="username">u/{author}</span>' if author else ""

    domain = _extract_domain(url)
    domain_html = f'<span class="domain-note">{domain}</span>' if domain else ""

    return f"""
<a href="{url}" target="_blank" class="card-link">
<div class="card cat-{cat['css']} src-{src_key}">
  <div class="card-top-bar"></div>
  <div class="card-inner">
    <div class="card-header">
      <span class="flag">{flag}</span>
      <div class="user-info">
        <div class="country">{country}</div>
        {author_html}
      </div>
      <span class="cat-badge badge-{cat['css']}">{cat['label']}</span>
    </div>
    <p class="post-text">{display_text}</p>
    <div class="agent-caption">
      <strong>🤖</strong> {caption}
    </div>
    <div class="card-footer">
      <span class="source-badge badge-src-{src_key}">{src['icon']} {src['label']}</span>
      <div class="footer-right">
        {domain_html}
        {score_html}
        <span class="view-link">View Post →</span>
      </div>
    </div>
  </div>
</div>
</a>"""


def render_feed(items: list[dict], active_filter: str = "all") -> str:
    if not items:
        return '<div class="empty-state">🔍 No stories yet — hit the button to find some!</div>'

    # Only show cards from social platforms
    social = [i for i in items if i.get("source_key") in SOCIAL_SOURCES]

    filtered = social if active_filter == "all" else [
        i for i in social if i["category_key"] == active_filter
    ]

    if not filtered:
        return '<div class="empty-state">No stories in this category yet.</div>'

    cards = "\n".join(render_card(i) for i in filtered)
    return f'<div class="feed">{cards}</div>'


STYLES = """
<style>
:root {
  --bg: #0f0f1a;
  --card-bg: #16213e;
  --card-border: rgba(255,255,255,0.08);
  --text: #e8e8e8;
  --muted: #888;
  --gold: #e8b84b;
}

.feed { display: flex; flex-direction: column; gap: 14px; padding: 4px 0; }

.card-link { text-decoration: none; display: block; }
.card-link:hover .card { border-color: rgba(232,184,75,0.4); transform: translateY(-1px); transition: all 0.15s; }

.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.card-top-bar { height: 3px; }
.cat-funny .card-top-bar    { background: linear-gradient(90deg, #f093fb, #f5576c); }
.cat-heartwarming .card-top-bar { background: linear-gradient(90deg, #ff6b6b, #feca57); }
.cat-food .card-top-bar     { background: linear-gradient(90deg, #a8edea, #fed6e3); }
.cat-culture .card-top-bar  { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.cat-stadium .card-top-bar  { background: linear-gradient(90deg, #43e97b, #38f9d7); }
.cat-match .card-top-bar    { background: linear-gradient(90deg, #f7971e, #ffd200); }
.cat-other .card-top-bar    { background: linear-gradient(90deg, #a18cd1, #fbc2eb); }

/* left accent by source */
.card { border-left: 3px solid transparent; }
.src-reddit    { border-left-color: #ff4500; }
.src-twitter   { border-left-color: #1d9bf0; }
.src-instagram { border-left-color: #e1306c; }
.src-facebook  { border-left-color: #1877f2; }
.src-news      { border-left-color: #a78bfa; }
.src-web       { border-left-color: #555; }

.card-inner { padding: 14px; }

.card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.flag { font-size: 26px; line-height: 1; }
.user-info { flex: 1; min-width: 0; }
.country { font-size: 13px; font-weight: 700; color: #fff; }
.username { font-size: 11px; color: var(--muted); }

.cat-badge {
  font-size: 10px; font-weight: 700; padding: 3px 8px;
  border-radius: 20px; white-space: nowrap;
  text-transform: uppercase; letter-spacing: 0.4px;
}
.badge-funny       { background: rgba(240,147,251,0.15); color: #f093fb; }
.badge-heartwarming{ background: rgba(255,107,107,0.15); color: #ff9f9f; }
.badge-food        { background: rgba(168,237,234,0.15); color: #a8edea; }
.badge-culture     { background: rgba(79,172,254,0.15);  color: #4facfe; }
.badge-stadium     { background: rgba(67,233,123,0.15);  color: #43e97b; }
.badge-match       { background: rgba(247,151,30,0.15);  color: #f7971e; }
.badge-other       { background: rgba(161,140,209,0.15); color: #a18cd1; }

.post-text {
  font-size: 14px; line-height: 1.55; color: var(--text);
  margin-bottom: 10px;
}

.agent-caption {
  background: rgba(255,255,255,0.04);
  border-left: 3px solid var(--gold);
  border-radius: 0 8px 8px 0;
  padding: 7px 10px; margin-bottom: 10px;
  font-size: 12px; color: #bbb; font-style: italic;
}
.agent-caption strong { font-style: normal; }

.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 6px;
}
.source-badge {
  font-size: 11px; font-weight: 600; padding: 3px 9px;
  border-radius: 20px; display: flex; align-items: center; gap: 4px;
}
.badge-src-reddit    { background: rgba(255,69,0,0.15);   color: #ff6b35; }
.badge-src-twitter   { background: rgba(29,155,240,0.15);  color: #5bb8f5; }
.badge-src-instagram { background: rgba(225,48,108,0.15);  color: #e1306c; }
.badge-src-facebook  { background: rgba(24,119,242,0.15);  color: #4a90e2; }
.badge-src-news      { background: rgba(167,139,250,0.15); color: #a78bfa; }
.badge-src-web       { background: rgba(100,100,100,0.15); color: #999; }

.indirect-note { font-size: 9px; opacity: 0.7; margin-left: 3px; }
.footer-right { display: flex; align-items: center; gap: 10px; }
.reaction { font-size: 11px; color: var(--muted); }
.domain-note { font-size: 11px; color: #666; font-style: italic; }
.view-link {
  font-size: 12px; font-weight: 700; color: var(--gold);
  text-decoration: none;
}
.view-link:hover { text-decoration: underline; }

.empty-state {
  text-align: center; padding: 48px 20px;
  color: var(--muted); font-size: 15px;
  font-family: -apple-system, sans-serif;
}
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
