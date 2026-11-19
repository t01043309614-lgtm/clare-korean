"""Pre-render the card content of index.html into static HTML.

The page draws its cards with JavaScript. Search engines and link previews
read the raw HTML, so this script opens the page in a headless browser,
collects what the JavaScript renders (every tab, not only the first one),
and writes it inside each container between <!-- prerender:ID --> markers.
On page load the JavaScript clears these containers and renders as usual,
so the look and behavior (tabs, flip, audio) do not change.

Run it again after adding or editing cards:
    python tools/prerender.py
"""
import functools
import http.server
import pathlib
import re
import socketserver
import threading

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

# Containers whose content is rendered by JavaScript.
CONTAINERS = ["tabs", "cardsGrid", "grammarList", "reactionsList",
              "situationalTabs", "situationalList", "pairsGroups", "quizList"]

COLLECT_JS = """() => {
  const out = {};
  const html = id => document.getElementById(id).innerHTML;
  // Tabbed containers: click through every tab and join all of them.
  const allTabs = (tabsId, listId) => {
    const buttons = document.querySelectorAll('#' + tabsId + ' .tab-btn');
    let joined = '';
    buttons.forEach(b => { b.click(); joined += html(listId); });
    buttons[0].click();
    return joined;
  };
  out.cardsGrid = allTabs('tabs', 'cardsGrid');
  out.situationalList = allTabs('situationalTabs', 'situationalList');
  for (const id of ['tabs', 'grammarList', 'reactionsList', 'situationalTabs', 'pairsGroups', 'quizList']) {
    out[id] = html(id);
  }
  return out;
}"""


def collect():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html")
            page.wait_for_load_state("networkidle")
            if errors:
                raise SystemExit("JavaScript error, nothing written: " + "; ".join(errors))
            result = page.evaluate(COLLECT_JS)
            browser.close()
            return result
    finally:
        srv.shutdown()


def inject(src, rendered):
    for cid in CONTAINERS:
        start, end = f"<!-- prerender:{cid} -->", f"<!-- /prerender:{cid} -->"
        block = start + rendered[cid] + end
        if start in src:
            src = re.sub(re.escape(start) + ".*?" + re.escape(end),
                         lambda m: block, src, count=1, flags=re.S)
        else:
            pattern = re.compile(r'(<(\w+)[^>]*\bid="' + cid + r'"[^>]*>)\s*(</\2>)')
            src, n = pattern.subn(lambda m: m.group(1) + block + m.group(3), src, count=1)
            if n != 1:
                raise SystemExit(f"Container #{cid} not found or not empty")
    return src


CARD_CLASSES = ("flip-card", "grammar-card", "reaction-card")


def check_notranslate(src):
    """Return a list of problems that would let phone browsers auto-translate
    the Korean, romanization, or English meanings on the cards."""
    problems = []
    if not re.search(r'<meta name="google" content="notranslate">', src):
        problems.append('<meta name="google" content="notranslate"> is missing from <head>')
    if not re.search(r'<html lang="en">', src):
        problems.append('<html lang="en"> is missing')
    for cid in CONTAINERS:
        m = re.search(r'<\w+[^>]*\bid="' + cid + r'"[^>]*>', src)
        if not m or 'translate="no"' not in m.group(0):
            problems.append(f'#{cid} container has no translate="no"')
    for cls in CARD_CLASSES:
        tags = re.findall(r'<\w+ class="' + cls + r'[ "][^>]*>', src)
        bad = [t for t in tags if 'translate="no"' not in t]
        if bad:
            problems.append(f'{len(bad)} of {len(tags)} .{cls} cards have no translate="no"')
        js = re.findall(r'card\.className = "' + cls + r'[^\n]*\n\s*card\.setAttribute\("translate", "no"\);', src)
        if f'card.className = "{cls}' in src and not js:
            problems.append(f'JS builder for .{cls} does not set translate="no"')
    # Site rule: romanization follows the National Institute of Korean Language
    # system and never uses hyphens.
    script = src[src.index("<script>"):] if "<script>" in src else src
    for rr in re.findall(r'\brr:\s*"([^"]*-[^"]*)"', script):
        problems.append(f'romanization has a hyphen: "{rr}"')
    return problems


def report(problems):
    if problems:
        print("WARNING: site rules are broken:")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print('Site rules OK: notranslate meta + translate="no" on all cards, no hyphens in romanization.')


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:
        # Quick check only, no browser:  python tools/prerender.py --check
        report(check_notranslate(INDEX.read_text(encoding="utf-8")))
        raise SystemExit(0)
    rendered = collect()
    src = INDEX.read_text(encoding="utf-8")
    out = inject(src, rendered)
    INDEX.write_text(out, encoding="utf-8", newline="")
    print("Pre-rendered:", ", ".join(f"{k} ({len(rendered[k])} chars)" for k in CONTAINERS))
    report(check_notranslate(out))
