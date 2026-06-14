import gradio as gr
import os
import time
from agents import run_stories_pipeline, run_match_pipeline
from ui import render_feed, STYLES, render_status

# ── state ──────────────────────────────────────────────────────────────────
stories_cache: list[dict] = []
match_cache: list[dict] = []
last_stories_refresh: float = 0
last_match_refresh: float = 0
REFRESH_COOLDOWN = 3600  # 1 hour in seconds

FILTERS = [
    ("All", "all"),
    ("Funny", "funny"),
    ("Heartwarming", "heartwarming"),
    ("Food Shock", "food"),
    ("Culture", "culture"),
    ("Stadium", "stadium"),
]

MATCH_FILTERS = [
    ("All", "all"),
    ("Match Buzz", "match"),
    ("Heartwarming", "heartwarming"),
    ("Funny", "funny"),
]

HEADER_HTML = f"""{STYLES}
<div style="text-align:center;padding:20px 16px 12px;
  background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
  border-radius:12px;margin-bottom:16px;font-family:-apple-system,sans-serif;">
  <h1 style="font-size:26px;font-weight:900;margin:0;color:#fff;letter-spacing:-0.5px;">
    World In The Stands
  </h1>
  <p style="color:#aaa;font-size:13px;margin:6px 0 0;">
    World Cup 2026 · Real fan stories from Reddit, X, Instagram & Facebook
  </p>
  <div style="display:inline-flex;align-items:center;gap:5px;margin-top:8px;
    background:rgba(255,60,60,0.15);border:1px solid rgba(255,60,60,0.3);
    color:#ff6b6b;font-size:11px;font-weight:700;padding:3px 12px;border-radius:20px;">
    <span style="width:6px;height:6px;background:#ff4444;border-radius:50%;
      display:inline-block;animation:blink 1.2s infinite;"></span>
    LIVE · AI-Curated
  </div>
  <style>@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}</style>
</div>"""

SOURCE_LEGEND = """
<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;font-family:-apple-system,sans-serif;">
  <span style="font-size:11px;color:#888;align-self:center;">Sources:</span>
  <span style="font-size:11px;background:rgba(255,69,0,0.15);color:#ff6b35;padding:3px 10px;border-radius:20px;font-weight:600;">Reddit</span>
  <span style="font-size:11px;background:rgba(29,155,240,0.15);color:#5bb8f5;padding:3px 10px;border-radius:20px;font-weight:600;">X / Twitter</span>
  <span style="font-size:11px;background:rgba(225,48,108,0.15);color:#e1306c;padding:3px 10px;border-radius:20px;font-weight:600;">Instagram</span>
  <span style="font-size:11px;background:rgba(24,119,242,0.15);color:#4a90e2;padding:3px 10px;border-radius:20px;font-weight:600;">Facebook</span>
  <span style="font-size:11px;color:#666;align-self:center;">· click any card to open</span>
</div>"""


def _mins_until_next(last: float) -> int:
    return max(0, int((REFRESH_COOLDOWN - (time.time() - last)) / 60) + 1)


def auto_load_stories():
    """Runs once on page load if cache is empty."""
    global stories_cache, last_stories_refresh
    if stories_cache:
        return render_status(f"{len(stories_cache)} stories loaded", is_loading=False), render_feed(stories_cache, "all")
    stories_cache = run_stories_pipeline()
    last_stories_refresh = time.time()
    return render_status(f"{len(stories_cache)} stories loaded", is_loading=False), render_feed(stories_cache, "all")


def refresh_stories():
    global stories_cache, last_stories_refresh
    if stories_cache and (time.time() - last_stories_refresh) < REFRESH_COOLDOWN:
        mins = _mins_until_next(last_stories_refresh)
        status = render_status(f"Next refresh available in {mins} min", is_loading=False)
        yield status, render_feed(stories_cache, "all"), FILTERS[0][0]
        return

    status = render_status("Searching Reddit for fan stories...")
    yield status, render_feed(stories_cache, "all"), FILTERS[0][0]

    stories_cache = run_stories_pipeline()
    last_stories_refresh = time.time()
    status = render_status(f"{len(stories_cache)} stories loaded", is_loading=False)
    yield status, render_feed(stories_cache, "all"), FILTERS[0][0]


def refresh_match():
    global match_cache, last_match_refresh
    if match_cache and (time.time() - last_match_refresh) < REFRESH_COOLDOWN:
        mins = _mins_until_next(last_match_refresh)
        status = render_status(f"Next refresh available in {mins} min", is_loading=False)
        yield status, render_feed(match_cache, "all"), MATCH_FILTERS[0][0]
        return

    status = render_status("Searching Reddit for match reactions...")
    yield status, render_feed(match_cache, "all"), MATCH_FILTERS[0][0]

    match_cache = run_match_pipeline()
    last_match_refresh = time.time()
    status = render_status(f"{len(match_cache)} match stories loaded", is_loading=False)
    yield status, render_feed(match_cache, "all"), MATCH_FILTERS[0][0]


def filter_stories(active_filter: str):
    return render_feed(stories_cache, active_filter)


def filter_match(active_filter: str):
    return render_feed(match_cache, active_filter)


# ── UI ─────────────────────────────────────────────────────────────────────
_theme = gr.themes.Base(
    primary_hue="yellow",
    neutral_hue="slate",
).set(
    body_background_fill="#0f0f1a",
    block_background_fill="#16213e",
    block_border_color="rgba(255,255,255,0.08)",
    input_background_fill="#1a1a2e",
)

_css = """
.gradio-container { max-width: 640px !important; margin: 0 auto !important; }
footer { display: none !important; }
.tab-nav button { font-size: 14px !important; font-weight: 700 !important; }
.refresh-btn { border-radius: 50px !important; font-size: 15px !important; font-weight: 800 !important; letter-spacing: 0.3px !important; }
"""

with gr.Blocks(title="World In The Stands") as demo:

    gr.HTML(HEADER_HTML)
    gr.HTML(SOURCE_LEGEND)

    with gr.Tabs():

        # ── Tab 1: Fan Stories ─────────────────────────────────────────────
        with gr.Tab("Fan Stories"):
            story_btn = gr.Button(
                "↻  Refresh Stories",
                variant="primary",
                size="lg",
                elem_classes=["refresh-btn"],
            )
            story_status = gr.HTML(
                render_status("Loading fan stories...", is_loading=True)
            )
            story_filter = gr.Radio(
                choices=[f[0] for f in FILTERS],
                value=FILTERS[0][0],
                label="Filter by",
                interactive=True,
            )
            story_feed = gr.HTML()

            story_btn.click(
                fn=refresh_stories,
                inputs=[],
                outputs=[story_status, story_feed, story_filter],
            )
            story_filter.change(
                fn=lambda f: filter_stories(
                    next((v for l, v in FILTERS if l == f), "all")
                ),
                inputs=[story_filter],
                outputs=[story_feed],
            )

        # ── Tab 2: Match Buzz ──────────────────────────────────────────────
        with gr.Tab("Match Buzz"):
            match_btn = gr.Button(
                "↻  Refresh Match Buzz",
                variant="primary",
                size="lg",
                elem_classes=["refresh-btn"],
            )
            match_status = gr.HTML(
                render_status("Click above to load match reactions", is_loading=False)
            )
            match_filter = gr.Radio(
                choices=[f[0] for f in MATCH_FILTERS],
                value=MATCH_FILTERS[0][0],
                label="Filter by",
                interactive=True,
            )
            match_feed = gr.HTML()

            match_btn.click(
                fn=refresh_match,
                inputs=[],
                outputs=[match_status, match_feed, match_filter],
            )
            match_filter.change(
                fn=lambda f: filter_match(
                    next((v for l, v in MATCH_FILTERS if l == f), "all")
                ),
                inputs=[match_filter],
                outputs=[match_feed],
            )

    gr.HTML("""
    <div style="text-align:center;padding:20px 16px;color:#555;font-size:11px;font-family:-apple-system,sans-serif;border-top:1px solid rgba(255,255,255,0.06);margin-top:8px;">
      &copy; 2026 gaamaa &nbsp;·&nbsp; Powered by Claude AI &nbsp;·&nbsp; World Cup 2026
    </div>""")

    # Auto-load stories on first visit
    demo.load(
        fn=auto_load_stories,
        inputs=[],
        outputs=[story_status, story_feed],
    )


if __name__ == "__main__":
    demo.launch()
