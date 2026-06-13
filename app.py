import gradio as gr
import os
from agents import run_stories_pipeline, run_match_pipeline
from ui import render_feed, STYLES, render_status

# ── state ──────────────────────────────────────────────────────────────────
stories_cache: list[dict] = []
match_cache: list[dict] = []

FILTERS = [
    ("🌐 All", "all"),
    ("😂 Funny", "funny"),
    ("❤️ Heartwarming", "heartwarming"),
    ("🍔 Food Shock", "food"),
    ("😲 Culture", "culture"),
    ("🏟️ Stadium", "stadium"),
]

MATCH_FILTERS = [
    ("🌐 All", "all"),
    ("🎉 Match Buzz", "match"),
    ("❤️ Heartwarming", "heartwarming"),
    ("😂 Funny", "funny"),
]

HEADER_HTML = f"""{STYLES}
<div style="text-align:center;padding:20px 16px 12px;
  background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
  border-radius:12px;margin-bottom:16px;font-family:-apple-system,sans-serif;">
  <h1 style="font-size:26px;font-weight:900;margin:0;color:#fff;letter-spacing:-0.5px;">
    🌎 World In The Stands ⚽
  </h1>
  <p style="color:#aaa;font-size:13px;margin:6px 0 0;">
    World Cup 2026 · Real fan stories curated by AI agents
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
  <span style="font-size:11px;background:rgba(255,69,0,0.15);color:#ff6b35;padding:3px 10px;border-radius:20px;font-weight:600;">🟠 Reddit — direct link</span>
  <span style="font-size:11px;background:rgba(29,155,240,0.15);color:#5bb8f5;padding:3px 10px;border-radius:20px;font-weight:600;">🐦 Twitter/X — direct link</span>
  <span style="font-size:11px;background:rgba(167,139,250,0.15);color:#a78bfa;padding:3px 10px;border-radius:20px;font-weight:600;">📰 Article — quotes post</span>
  <span style="font-size:11px;background:rgba(100,100,100,0.15);color:#999;padding:3px 10px;border-radius:20px;font-weight:600;">🔗 Web — via search</span>
</div>"""


def refresh_stories(active_filter: str):
    global stories_cache
    status = render_status("Scout Agent searching web & Reddit for fan stories…")
    yield status, render_feed(stories_cache, active_filter)

    stories_cache = run_stories_pipeline()
    status = render_status(f"✅ {len(stories_cache)} stories found", is_loading=False)
    yield status, render_feed(stories_cache, active_filter)


def refresh_match(active_filter: str):
    global match_cache
    status = render_status("Scout Agent searching for match reactions & buzz…")
    yield status, render_feed(match_cache, active_filter)

    match_cache = run_match_pipeline()
    status = render_status(f"✅ {len(match_cache)} match stories found", is_loading=False)
    yield status, render_feed(match_cache, active_filter)


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
"""

with gr.Blocks(title="World In The Stands ⚽") as demo:

    gr.HTML(HEADER_HTML)
    gr.HTML(SOURCE_LEGEND)

    with gr.Tabs():

        # ── Tab 1: Fan Stories ─────────────────────────────────────────────
        with gr.Tab("🌍 Fan Stories"):
            with gr.Row():
                story_filter = gr.Radio(
                    choices=[f[0] for f in FILTERS],
                    value="🌐 All",
                    label="Filter",
                    interactive=True,
                )
            story_status = gr.HTML(
                render_status("Click below to load fan stories", is_loading=False)
            )
            story_feed = gr.HTML(
                '<div style="text-align:center;color:#888;padding:40px;font-family:sans-serif;">Hit the button to discover stories ⚽</div>'
            )
            story_btn = gr.Button(
                "⚡ Find Fan Stories",
                variant="primary",
                size="lg",
            )

            story_btn.click(
                fn=refresh_stories,
                inputs=[story_filter],
                outputs=[story_status, story_feed],
            )
            story_filter.change(
                fn=lambda f: filter_stories(
                    next((v for l, v in FILTERS if l == f), "all")
                ),
                inputs=[story_filter],
                outputs=[story_feed],
            )

        # ── Tab 2: Match Buzz ──────────────────────────────────────────────
        with gr.Tab("🎉 Match Buzz"):
            with gr.Row():
                match_filter = gr.Radio(
                    choices=[f[0] for f in MATCH_FILTERS],
                    value="🌐 All",
                    label="Filter",
                    interactive=True,
                )
            match_status = gr.HTML(
                render_status("Click below to load match reactions", is_loading=False)
            )
            match_feed = gr.HTML(
                '<div style="text-align:center;color:#888;padding:40px;font-family:sans-serif;">Hit the button to see match reactions ⚽</div>'
            )
            match_btn = gr.Button(
                "⚡ Find Match Reactions",
                variant="primary",
                size="lg",
            )

            match_btn.click(
                fn=refresh_match,
                inputs=[match_filter],
                outputs=[match_status, match_feed],
            )
            match_filter.change(
                fn=lambda f: filter_match(
                    next((v for l, v in MATCH_FILTERS if l == f), "all")
                ),
                inputs=[match_filter],
                outputs=[match_feed],
            )

    gr.HTML("""
    <div style="text-align:center;padding:16px;color:#555;font-size:11px;font-family:sans-serif;">
      Built with Claude AI · Sources: Reddit & Web Search · World Cup 2026 🏆
    </div>""")


if __name__ == "__main__":
    demo.launch(theme=_theme, css=_css)
