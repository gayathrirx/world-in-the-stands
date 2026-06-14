import gradio as gr
import os
import time
import json
from pathlib import Path
from agents import run_stories_pipeline
from ui import render_feed, STYLES, render_status

STORIES_CACHE_FILE = Path("stories_cache.json")
REFRESH_COOLDOWN   = 3600  # 1 hour


def _save(path: Path, data: list):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Cache save error: {e}")


def _load(path: Path) -> list:
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except Exception as e:
        print(f"Cache load error: {e}")
    return []


# ── state ──────────────────────────────────────────────────────────────────
stories_cache: list[dict] = _load(STORIES_CACHE_FILE)
last_stories_refresh: float = STORIES_CACHE_FILE.stat().st_mtime if STORIES_CACHE_FILE.exists() else 0

FILTERS = [
    ("All", "all"),
    ("Funny", "funny"),
    ("Heartwarming", "heartwarming"),
    ("Food Shock", "food"),
    ("Culture", "culture"),
    ("Stadium", "stadium"),
]

HEADER_HTML = f"""{STYLES}
<div style="text-align:center;padding:20px 16px 12px;
  background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
  border-radius:12px;margin-bottom:16px;font-family:-apple-system,sans-serif;">
  <h1 style="font-size:26px;font-weight:900;margin:0;color:#fff;letter-spacing:-0.5px;">
    World In The Stands
  </h1>
  <p style="color:#aaa;font-size:13px;margin:6px 0 0;">
    Real fan stories · World In The Stands
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

FOOTER_HTML = """
<div style="text-align:center;padding:20px 16px;color:#555;font-size:11px;
  font-family:-apple-system,sans-serif;border-top:1px solid rgba(255,255,255,0.06);
  margin-top:8px;">
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-bottom:10px;">
    <span style="color:#888;">Sources:</span>
    <span style="background:rgba(255,69,0,0.15);color:#ff6b35;padding:2px 10px;border-radius:20px;font-weight:600;">Reddit</span>
    <span style="background:rgba(29,155,240,0.15);color:#5bb8f5;padding:2px 10px;border-radius:20px;font-weight:600;">X / Twitter</span>
    <span style="background:rgba(225,48,108,0.15);color:#e1306c;padding:2px 10px;border-radius:20px;font-weight:600;">Instagram</span>
    <span style="background:rgba(24,119,242,0.15);color:#4a90e2;padding:2px 10px;border-radius:20px;font-weight:600;">Facebook</span>
  </div>
  &copy; 2026 gaamaa &nbsp;·&nbsp; Powered by Claude AI &nbsp;·&nbsp; World In The Stands
</div>"""


def _mins_until_next(last: float) -> int:
    return max(0, int((REFRESH_COOLDOWN - (time.time() - last)) / 60) + 1)


def _stories_html(filter_key="all"):
    return render_status(f"{len(stories_cache)} stories loaded", is_loading=False) + render_feed(stories_cache, filter_key)


def auto_load_stories():
    global stories_cache, last_stories_refresh
    if stories_cache:
        return _stories_html()
    # no cache — fetch in foreground (first cold start)
    yield render_status("Finding fan stories from around the world...", is_loading=True)
    stories_cache = run_stories_pipeline()
    last_stories_refresh = time.time()
    _save(STORIES_CACHE_FILE, stories_cache)
    yield _stories_html()


def refresh_stories():
    global stories_cache, last_stories_refresh
    # only enforce cooldown if we already have stories to show
    if stories_cache and (time.time() - last_stories_refresh) < REFRESH_COOLDOWN:
        mins = _mins_until_next(last_stories_refresh)
        yield render_status(f"Come back in {mins} min — the AI is on a budget (tokens aren't free, people!)", is_loading=False) + render_feed(stories_cache, "all"), _filter_bar_html("all")
        return

    yield render_status("Searching for fan stories...") + render_feed(stories_cache, "all"), _filter_bar_html("all")

    stories_cache = run_stories_pipeline()
    last_stories_refresh = time.time()
    _save(STORIES_CACHE_FILE, stories_cache)
    yield _stories_html(), _filter_bar_html("all")


def filter_stories(active_filter: str):
    key = next((v for l, v in FILTERS if l == active_filter), "all")
    return _stories_html(key)


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
/* hide the hidden textbox */
.filter-state { display: none !important; }
/* control bar */
.ctrl-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 0 2px; }
.filter-chips { display: flex; gap: 6px; overflow-x: auto; flex: 1; scrollbar-width: none; }
.filter-chips::-webkit-scrollbar { display: none; }
.chip {
  flex-shrink: 0; cursor: pointer; border: 2px solid rgba(255,255,255,0.18);
  background: transparent; color: #bbb; border-radius: 50px;
  padding: 0 16px; height: 38px; font-size: 13px; font-weight: 700;
  font-family: -apple-system, sans-serif; white-space: nowrap; transition: all 0.15s;
}
.chip:hover { border-color: rgba(255,255,255,0.35); color: #fff; }
.chip.active { background: #e8b84b; border-color: #e8b84b; color: #000; }
.refresh-btn { flex-shrink: 0; border-radius: 50px !important; font-size: 13px !important; font-weight: 700 !important; height: 38px !important; white-space: nowrap !important; min-width: unset !important; padding: 0 18px !important; }
"""

FILTER_BAR_JS = """
<div class="ctrl-bar">
  <div class="filter-chips" id="filter-chips">
    {chips}
  </div>
</div>
"""


def _filter_bar_html(active="all"):
    chips = "".join(
        f'<button class="chip{" active" if v == active else ""}" data-val="{v}">{l}</button>'
        for l, v in FILTERS
    )
    return FILTER_BAR_JS.format(chips=chips)


_head = """
<script>
document.addEventListener('click', function(e) {
  var chip = e.target.closest('.chip');
  if (!chip) return;
  document.querySelectorAll('.chip').forEach(function(c) { c.classList.remove('active'); });
  chip.classList.add('active');
  var tb = document.querySelector('.filter-state textarea');
  if (tb) {
    var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(tb, chip.dataset.val);
    tb.dispatchEvent(new Event('input', { bubbles: true }));
  }
});
</script>
"""

with gr.Blocks(title="World In The Stands", head=_head) as demo:

    gr.HTML(HEADER_HTML)

    filter_bar = gr.HTML(_filter_bar_html("all"))
    filter_state = gr.Textbox(value="all", visible=False, elem_classes=["filter-state"])

    with gr.Row():
        story_btn = gr.Button("↻ Refresh", variant="primary", size="sm", elem_classes=["refresh-btn"])

    story_out = gr.HTML(render_status("Loading stories...", is_loading=True))

    gr.HTML(FOOTER_HTML)

    story_btn.click(fn=refresh_stories, inputs=[], outputs=[story_out, filter_bar])
    filter_state.change(fn=lambda v: _stories_html(v), inputs=[filter_state], outputs=[story_out])
    demo.load(fn=auto_load_stories, inputs=[], outputs=[story_out])


if __name__ == "__main__":
    demo.launch()
