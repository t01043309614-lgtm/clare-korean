"""Build the free Level 1 workbook PDF from the cards in index.html.

Review pages read the Everyday Korean and Situational Phrases data straight
from index.html, so they stay in sync with the site. The exercises below use
sentences that already exist in those two sections.

Run again after editing:
    python tools/build_workbook.py
Output: assets/workbook/level1-everyday-korean.pdf
"""
import html
import pathlib
import re

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUT = ROOT / "assets" / "workbook" / "level1-everyday-korean.pdf"
SITE = "clare-korean-flashcards.netlify.app"

FIELD = re.compile(r'(\w+):"((?:[^"\\]|\\.)*)"')

# Level 1 covers the first 18 Everyday Korean cards (the set in the published
# workbook). Newer cards (Topic19+) join the workbook only when Clare asks.
LEVEL1_EVERYDAY_COUNT = 18


def parse_entries(block):
    """Each card/phrase is a `{ kr:"..", en:"..", ... }` object; nested
    `example:{...}` objects are folded into the parent."""
    out = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("{ ") and "kr:" in line:
            out.append(dict(FIELD.findall(line.split("example:")[0])))
    return out


def load_data():
    src = INDEX.read_text(encoding="utf-8")
    every = src[src.index('id: "everyday"'):src.index('id: "real"')]
    everyday = parse_entries(every)[:LEVEL1_EVERYDAY_COUNT]
    sit = src[src.index("var situationalData = ["):]
    sit = sit[:sit.index("\n  ];")]
    cats = []
    for chunk in sit.split('      id: "')[1:]:
        cats.append({
            "kr": re.search(r'labelKr: "([^"]+)"', chunk).group(1),
            "en": re.search(r'labelEn: "([^"]+)"', chunk).group(1),
            "phrases": parse_entries(chunk),
        })
    return everyday, cats


# ---- Exercises (all sentences come from the site's existing cards) ----
# Part 1: (sentence with ___, answer, English of the full sentence)
FILL_EVERYDAY = [
    ("여기요, ___!", "도와주세요", "Excuse me, please help me!"),
    ("___, 시간 없어요!", "빨리요", "Quickly, we don't have time!"),
    ("___, 잘 모르겠어요.", "글쎄요", "Well, I'm not really sure."),
    ("___, 제가 할게요.", "아니에요", "No, no, I'll do it."),
    ("___ 제 말은요...", "그러니까", "So, what I mean is..."),
    ("___ 좀 아닌 것 같아요.", "그건", "I don't think that's quite right."),
]
FILL_SITUATIONAL = [
    ("아메리카노 한 ___ 주세요.", "잔", "One americano, please.", "Cafe"),
    ("얼음 ___.", "빼주세요", "No ice, please.", "Cafe"),
    ("이거 ___?", "얼마예요", "How much is this?", "Convenience Store"),
    ("여기서 ___.", "세워주세요", "Please stop here.", "Taxi"),
    ("___ 어디예요?", "화장실이", "Where is the bathroom?", "Asking Directions"),
    ("반찬 ___ 주세요.", "더", "More side dishes, please.", "Restaurant"),
    ("___해 주세요.", "계산", "Check, please.", "Restaurant"),
    ("머리가 ___.", "아파요", "I have a headache.", "Pharmacy"),
    ("다른 ___ 있어요?", "색", "Do you have another color?", "Clothing Store"),
]
# Part 2: (English, answer, situation)
WRITING = [
    ("Thank you.", "감사합니다", "Everyday"),
    ("Long time no see.", "오랜만이에요", "Everyday"),
    ("Do you take card?", "카드 되나요?", "Convenience Store"),
    ("Please take me to this address.", "이 주소로 가주세요.", "Taxi"),
    ("Is there a subway station nearby?", "이 근처에 지하철역 있어요?", "Asking Directions"),
    ("Do you have cold medicine?", "감기약 있어요?", "Pharmacy"),
    ("Can I try it on?", "입어 봐도 돼요?", "Clothing Store"),
    ("I'm just looking.", "그냥 구경하는 거예요.", "Clothing Store"),
]
# Part 3: (Korean, question, options, answer index)
QUIZ = [
    ("얼음 빼주세요.", "What does the customer want?",
     ["More ice", "No ice", "A bigger size"], 1),
    ("여기서 드실 거예요, 가져가실 거예요?", "What is the staff asking?",
     ["For here or to go?", "What size?", "How many people?"], 0),
    ("영수증 필요 없어요.", "What doesn't the speaker need?",
     ["A bag", "A receipt", "A card"], 1),
    ("데워 드릴까요?", "What is the clerk offering to do?",
     ["Heat it up", "Put it in a bag", "Give a discount"], 0),
    ("얼마나 걸려요?", "What is the passenger asking?",
     ["The price", "How long it will take", "Where to stop"], 1),
    ("몇 분이세요?", "What is the server asking?",
     ["How many people", "What to order", "How to pay"], 0),
    ("하루에 몇 번 먹어요?", "What is the speaker asking at the pharmacy?",
     ["How much it costs", "How many times a day to take it", "Where the pharmacy is"], 1),
    ("어디서 갈아타요?", "What is the speaker asking?",
     ["Where to get off", "Where to transfer", "Where to buy a ticket"], 1),
    ("오랜만이에요", "When do you say this?",
     ["Meeting someone for the first time", "Seeing someone after a long time", "Saying goodbye"], 1),
    ("별말씀을요", "What does it mean?",
     ["You're welcome", "Excuse me", "I'm sorry"], 0),
]

CSS = """
@page { size: A4; margin: 0; }
:root { --navy:#14162C; --coral:#FF6F5E; --off:#F4F4F6; --muted:#6B6E85; --line:#D9DAE3; }
* { box-sizing: border-box; }
body { margin:0; font-family:'Noto Sans KR','Malgun Gothic',sans-serif; color:var(--navy); background:#fff; }
.page { width:210mm; height:297mm; padding:20mm 18mm 18mm; position:relative; page-break-after:always; overflow:hidden; background:#fff; }
.page:last-child { page-break-after:auto; }
.foot { position:absolute; left:18mm; right:18mm; bottom:10mm; display:flex; justify-content:space-between;
        font-size:8.5pt; color:var(--muted); border-top:1px solid var(--line); padding-top:3mm; }
.kicker { display:inline-block; background:var(--coral); color:#fff; font-weight:700; font-size:8.5pt;
          letter-spacing:.14em; text-transform:uppercase; padding:1.5mm 4mm; border-radius:99px; }
h1 { font-size:24pt; margin:4mm 0 2mm; }
h2 { font-size:15pt; margin:0 0 3mm; }
.lead { color:var(--muted); font-size:10.5pt; margin:0 0 7mm; line-height:1.55; }
.cover { background:var(--navy); color:var(--off); display:flex; flex-direction:column; justify-content:space-between; }
.cover .brand { font-size:9pt; letter-spacing:.2em; text-transform:uppercase; color:var(--coral); font-weight:700; }
.cover h1 { font-size:40pt; line-height:1.1; margin:0 0 6mm; color:#fff; }
.cover .level { display:inline-block; border:1.5px solid var(--coral); color:var(--coral); border-radius:99px; padding:2mm 6mm; font-weight:700; font-size:11pt; }
.cover .sub { font-size:13pt; color:#C9CBE0; line-height:1.6; margin-top:8mm; }
.cover .bar { height:3mm; width:40mm; background:var(--coral); border-radius:2mm; margin-bottom:10mm; }
.cover .bottom { font-size:10pt; color:#C9CBE0; line-height:1.7; }
.box { background:var(--off); border-radius:4mm; padding:6mm 7mm; margin-bottom:5mm; }
.box h3 { margin:0 0 2mm; font-size:11.5pt; color:var(--coral); }
.box p { margin:0; font-size:10.5pt; line-height:1.6; }
.toc { list-style:none; padding:0; margin:0; }
.toc li { display:flex; justify-content:space-between; padding:3.2mm 0; border-bottom:1px dashed var(--line); font-size:11pt; }
.toc b { color:var(--coral); margin-right:3mm; }
table.review { width:100%; border-collapse:collapse; font-size:9.6pt; }
table.review th { background:var(--navy); color:#fff; text-align:left; padding:2.2mm 3mm; font-weight:700; }
table.review td { padding:2mm 3mm; border-bottom:1px solid var(--line); vertical-align:top; }
table.review tr:nth-child(even) td { background:var(--off); }
table.review td.kr { font-weight:700; font-size:10.5pt; }
table.review td.rr { color:var(--muted); font-style:italic; }
table.review tr.cat td { background:#fff; color:var(--coral); font-weight:700; padding-top:3.5mm; border-bottom:2px solid var(--coral); }
.bank { border:2px dashed var(--coral); border-radius:4mm; padding:4mm 6mm; margin-bottom:6mm; }
.bank .t { font-size:8.5pt; letter-spacing:.14em; text-transform:uppercase; color:var(--coral); font-weight:700; margin-bottom:2mm; }
.bank span { display:inline-block; background:var(--off); border-radius:99px; padding:1.2mm 4mm; margin:1mm 1.5mm 1mm 0; font-weight:700; font-size:11pt; }
.q { display:flex; gap:4mm; padding:4.5mm 0; border-bottom:1px solid var(--line); }
.num { flex:none; width:8mm; height:8mm; border-radius:50%; background:var(--navy); color:#fff; font-weight:700; font-size:10pt;
       display:flex; align-items:center; justify-content:center; }
.q .body { flex:1; }
.q .kr { font-size:14pt; font-weight:700; margin:0 0 1.5mm; }
.blank { display:inline-block; min-width:32mm; border-bottom:2px solid var(--coral); margin:0 1mm; }
.q .en { font-size:10pt; color:var(--muted); margin:0; }
.tag { display:inline-block; font-size:7.5pt; letter-spacing:.1em; text-transform:uppercase; color:var(--coral); font-weight:700; margin-bottom:1mm; }
.write .en-big { font-size:13pt; font-weight:700; margin:0 0 3mm; }
.lines div { height:11mm; border-bottom:1.2px solid var(--line); }
.opt { display:flex; align-items:center; gap:3mm; font-size:11pt; margin:2mm 0; }
.circle { width:6mm; height:6mm; border:1.5px solid var(--navy); border-radius:50%; flex:none; display:flex; align-items:center;
          justify-content:center; font-size:8.5pt; font-weight:700; }
.quiz .kr { background:var(--off); border-left:3px solid var(--coral); padding:2.5mm 4mm; border-radius:0 2mm 2mm 0; display:inline-block; }
.quiz .question { font-size:11pt; font-weight:700; margin:2.5mm 0 1mm; }
.opts { display:flex; flex-wrap:wrap; gap:1mm 8mm; }
.q.quiz { padding:3.5mm 0; }
.quiz .kr { font-size:13pt; padding:2mm 4mm; }
.quiz .question { margin:2mm 0 0.5mm; }
.quiz .opt { margin:1.2mm 0; }
.answers { columns:2; column-gap:8mm; font-size:10pt; }
.answers .grp { break-inside:avoid; margin-bottom:5mm; }
.answers h3 { font-size:11pt; color:var(--coral); margin:0 0 2mm; }
.answers ol { margin:0; padding-left:6mm; }
.answers li { margin:1.2mm 0; line-height:1.45; }
.answers .sm { color:var(--muted); }
.end { background:var(--navy); color:var(--off); display:flex; flex-direction:column; justify-content:center; align-items:flex-start; }
.end h1 { color:#fff; font-size:30pt; }
.end p { font-size:12pt; line-height:1.7; color:#C9CBE0; max-width:150mm; }
.end .url { margin-top:8mm; background:var(--coral); color:#fff; font-weight:700; padding:3mm 7mm; border-radius:99px; font-size:12pt; }
"""

e = html.escape


def page(inner, n, total, cls=""):
    foot = "" if cls in ("cover", "end") else (
        f'<div class="foot"><span>Clare\'s Korean · Level 1 Workbook</span><span>{n} / {total}</span></div>')
    return f'<section class="page {cls}">{inner}{foot}</section>'


def blankify(s):
    return e(s).replace("___", '<span class="blank">&nbsp;</span>')


def fill_page(items, start, title, lead, bank):
    rows = "".join(
        f'<div class="q"><div class="num">{start + i}</div><div class="body">'
        + (f'<span class="tag">{e(it[3])}</span>' if len(it) > 3 else "")
        + f'<p class="kr">{blankify(it[0])}</p><p class="en">{e(it[2])}</p></div></div>'
        for i, it in enumerate(items))
    bank_html = "".join(f"<span>{e(w)}</span>" for w in bank)
    return (f'<span class="kicker">Part 1 · Fill in the Blank</span><h2 style="margin-top:4mm">{e(title)}</h2>'
            f'<p class="lead">{e(lead)}</p><div class="bank"><div class="t">Word Bank</div>{bank_html}</div>{rows}')


def build_html():
    everyday, cats = load_data()
    pages = []

    pages.append(("cover", """
      <div><div class="brand">Stylish Korean Clare</div></div>
      <div><div class="bar"></div><h1>Clare's Korean<br>Workbook</h1>
        <span class="level">Level 1 · Everyday Korean &amp; Situational Phrases</span>
        <p class="sub">Real Korean for real conversations.<br>Review, fill in the blanks, write, and quiz yourself.</p></div>
      <div class="bottom">Free workbook · """ + SITE + """</div>"""))

    pages.append(("", """
      <span class="kicker">Start Here</span><h1>How to Use This Workbook</h1>
      <p class="lead">Every phrase in this workbook comes from the Everyday Korean and Situational Phrases cards on the Clare's Korean site.
      Listen to Clare's audio there, then practice here.</p>
      <div class="box"><h3>1. Review</h3><p>Read the phrase lists first. Say each Korean phrase out loud.</p></div>
      <div class="box"><h3>2. Fill in the Blank</h3><p>Pick the missing word from the word bank and complete the sentence.</p></div>
      <div class="box"><h3>3. Writing Practice</h3><p>Read the English and write the Korean by yourself. Try not to look back!</p></div>
      <div class="box"><h3>4. Mini Quiz</h3><p>Read the Korean and choose the best answer. Check your answers at the end.</p></div>
      <h2 style="margin-top:8mm">Contents</h2>
      <ul class="toc">
        <li><span><b>Review</b>Everyday Korean</span><span>3</span></li>
        <li><span><b>Review</b>Situational Phrases</span><span>4–6</span></li>
        <li><span><b>Part 1</b>Fill in the Blank (15)</span><span>7–9</span></li>
        <li><span><b>Part 2</b>Writing Practice (8)</span><span>10–11</span></li>
        <li><span><b>Part 3</b>Mini Quiz (10)</span><span>12–13</span></li>
        <li><span><b>Answers</b>Answer Key</span><span>14</span></li>
      </ul>"""))

    rows = "".join(
        f'<tr><td class="kr">{e(c["kr"])}</td><td class="rr">{e(c["rr"])}</td><td>{e(c["en"])}</td></tr>'
        for c in everyday)
    pages.append(("", '<span class="kicker">Review</span><h1>Everyday Korean</h1>'
                  '<p class="lead">Phrases you can use every day. Read each one out loud.</p>'
                  f'<table class="review"><tr><th>Korean</th><th>Romanization</th><th>English</th></tr>{rows}</table>'))

    def sit_table(cs):
        body = ""
        for c in cs:
            body += f'<tr class="cat"><td colspan="3">{e(c["kr"])} · {e(c["en"])}</td></tr>'
            body += "".join(
                f'<tr><td class="kr">{e(p["kr"])}</td><td class="rr">{e(p["rr"])}</td><td>{e(p["en"])}</td></tr>'
                for p in c["phrases"])
        return f'<table class="review">{body}</table>'
    for i in range(0, len(cats), 3):
        lead = "Real phrases for real situations." + (" (continued)" if i else "")
        pages.append(("", '<span class="kicker">Review</span><h1>Situational Phrases</h1>'
                      f'<p class="lead">{lead}</p>' + sit_table(cats[i:i + 3])))

    pages.append(("", fill_page(FILL_EVERYDAY, 1, "Everyday Korean",
                                "Choose the missing word from the word bank. The English shows the full meaning.",
                                sorted(a for _, a, _ in FILL_EVERYDAY))))
    s1, s2 = FILL_SITUATIONAL[:5], FILL_SITUATIONAL[5:]
    pages.append(("", fill_page(s1, 7, "Situational Phrases", "Choose the missing word from the word bank.",
                                sorted(x[1] for x in s1))))
    pages.append(("", fill_page(s2, 12, "Situational Phrases", "Choose the missing word from the word bank.",
                                sorted(x[1] for x in s2))))

    def write_page(items, start):
        qs = "".join(
            f'<div class="q write"><div class="num">{start + i}</div><div class="body">'
            f'<span class="tag">{e(sit)}</span><p class="en-big">{e(en)}</p>'
            f'<div class="lines"><div></div><div></div></div></div></div>'
            for i, (en, _, sit) in enumerate(items))
        return ('<span class="kicker">Part 2 · Writing Practice</span><h2 style="margin-top:4mm">Write It in Korean</h2>'
                '<p class="lead">Read the English and write the Korean phrase. Write it twice for extra practice.</p>' + qs)
    pages.append(("", write_page(WRITING[:4], 1)))
    pages.append(("", write_page(WRITING[4:], 5)))

    def quiz_page(items, start):
        qs = ""
        for i, (kr, q, opts, _) in enumerate(items):
            o = "".join(f'<div class="opt"><span class="circle">{"ABC"[j]}</span>{e(t)}</div>' for j, t in enumerate(opts))
            qs += (f'<div class="q quiz"><div class="num">{start + i}</div><div class="body">'
                   f'<p class="kr">{e(kr)}</p><p class="question">{e(q)}</p><div class="opts">{o}</div></div></div>')
        return ('<span class="kicker">Part 3 · Mini Quiz</span><h2 style="margin-top:4mm">Choose the Best Answer</h2>'
                '<p class="lead">Read the Korean, then circle A, B, or C.</p>' + qs)
    pages.append(("", quiz_page(QUIZ[:5], 1)))
    pages.append(("", quiz_page(QUIZ[5:], 6)))

    fill_all = [(s, a, en) for s, a, en, *_ in FILL_EVERYDAY + FILL_SITUATIONAL]
    ans1 = "".join(f'<li><b>{e(a)}</b> <span class="sm">— {e(s.replace("___", a))}</span></li>' for s, a, _ in fill_all)
    ans2 = "".join(f'<li><b>{e(a)}</b> <span class="sm">— {e(en)}</span></li>' for en, a, _ in WRITING)
    ans3 = "".join(f'<li><b>{"ABC"[k]}</b> <span class="sm">— {e(o[k])}</span></li>' for _, _, o, k in QUIZ)
    pages.append(("", '<span class="kicker">Answers</span><h1>Answer Key</h1>'
                  '<p class="lead">Check your answers. Then listen to the phrases on the site and repeat after Clare.</p>'
                  f'<div class="answers"><div class="grp"><h3>Part 1 · Fill in the Blank</h3><ol>{ans1}</ol></div>'
                  f'<div class="grp"><h3>Part 2 · Writing Practice</h3><ol>{ans2}</ol></div>'
                  f'<div class="grp"><h3>Part 3 · Mini Quiz</h3><ol>{ans3}</ol></div></div>'))

    pages.append(("end", f"""
      <span class="kicker">Great Job!</span><h1>잘했어요!</h1>
      <p>You finished the Level 1 workbook. Keep practicing with Clare's audio flashcards, grammar cards,
      situational phrases, and the listening quiz on the site.</p>
      <span class="url">{SITE}</span>"""))

    total = len(pages)
    body = "".join(page(inner, i + 1, total, cls) for i, (cls, inner) in enumerate(pages))
    for c in everyday + [p for cat in cats for p in cat["phrases"]]:
        if "-" in c["rr"]:
            raise SystemExit(f'Site rule: no hyphens in romanization. Fix "{c["rr"]}" in index.html first.')
    # Site rule: no auto-translation (notranslate meta + translate="no").
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="google" content="notranslate">'
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body translate="no">{body}</body></html>'), total


def main():
    doc, total = build_html()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(doc, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=str(OUT), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    print(f"Wrote {OUT.relative_to(ROOT)} ({total} pages)")


# =====================================================================
# Level 2 — Mini Dialogues, 맞다/나다, Body Expressions, Time Words.
# Same design (CSS, cover, review tables, answer key) as Level 1; Level 1
# code above is reused, not changed. Build with:
#     python tools/build_workbook.py --level 2
# Output: assets/workbook/level2-everyday-korean.pdf
# Korean, romanization and English come from the cards in index.html.
# =====================================================================
OUT2 = ROOT / "assets" / "workbook" / "level2-everyday-korean.pdf"
LINE = re.compile(r'^\s*\{ ')


def _objs(block):
    """Every `{ kr:"..", ... }` object in a block, one dict per object
    (example objects on their own line are returned separately)."""
    out = []
    for line in block.splitlines():
        for part in re.split(r'example:\{', line):
            d = dict(FIELD.findall(part))
            if "kr" in d:
                out.append(d)
    return out


def load_level2():
    src = INDEX.read_text(encoding="utf-8")
    script = src[src.index("<script>"):]

    dsrc = script[script.index("var dialoguesData = ["):]
    dsrc = dsrc[:dsrc.index("\n  ];")]
    dialogues = []
    for chunk in dsrc.split('{ title:"')[1:]:
        head = dict(FIELD.findall('title:"' + chunk.split("lines:")[0]))
        lines = [dict(FIELD.findall(l)) for l in chunk.splitlines() if 'speaker:"' in l]
        dialogues.append({**head, "lines": lines})

    def corner(title_start):
        c = script[script.index(f'title: "{title_start}'):]
        c = c[:c.index("\n        }")]
        cards = []
        for item in c.split("{ emoji:")[1:]:
            word, _, ex = item.partition("examples:")
            w = dict(FIELD.findall("emoji:" + word.split("meaning:")[0]))
            x = dict(FIELD.findall(ex))
            cards.append({"emoji": w["emoji"], "kr": w["kr"], "rr": w["rr"], "en": w["en"],
                          "ex_kr": x["kr"], "ex_rr": x["rr"], "ex_en": x["en"]})
        return cards

    def section(sid):
        c = script[script.index(f'id: "{sid}"'):]
        c = c[:c.index("\n      ]")]
        cards = []
        for line in c.splitlines():
            if 'example:{' in line:
                x = dict(FIELD.findall(line.split("example:{")[1]))
                cards[-1].update({"ex_kr": x["kr"], "ex_rr": x["rr"], "ex_en": x["en"]})
            elif LINE.match(line) and 'kr:"' in line:
                cards.append(dict(FIELD.findall(line)))
        return cards

    for dg in dialogues:  # JS strings escape quotes as \"
        for k, v in list(dg.items()):
            if isinstance(v, str):
                dg[k] = v.replace('\\"', '"')
    data = {"dialogues": dialogues, "matda": corner("맞다:"), "nada": corner("나다:"),
            "time": section("time"), "body": section("body")}
    rrs = [l["rr"] for d in dialogues for l in d["lines"]]
    for k in ("matda", "nada", "time", "body"):
        rrs += [c["rr"] for c in data[k]] + [c["ex_rr"] for c in data[k]]
    for rr in rrs:
        if "-" in rr:
            raise SystemExit(f'Site rule: no hyphens in romanization. Fix "{rr}" in index.html first.')
    return data


# ---- Level 2 exercises (Clare's script) ----
L2_LISTEN = [  # (dialogue no., question, options, answer index)
    (1, "What does B say when offered coffee?", ["Yes, please", "No, thanks", "Maybe later"], 1),
    (1, "What does A bring instead?", ["Tea", "Water", "Juice"], 1),
    (2, "What is A asking about?", ["Why B didn't answer the phone", "Where B is going", "What B ate"], 0),
    (2, "When will B call?", ["Now", "Later today", "Tomorrow"], 1),
    (3, "What does A wish B?", ["A good trip", "Good luck on the test", "A happy birthday"], 1),
    (3, "What does A give B?", ["Chocolate", "Taffy (엿)", "A pen"], 1),
]
L2_DICTATION = [  # (sentence with ___, answers, (dialogue no., line nos.))
    ("커피 ___? 아니요, ___.", ["드릴까요", "괜찮아요"], (1, [1, 2])),
    ("___ 전화할게요.", ["이따가"], (2, [2])),
    ("시험 ___ 봐!", ["잘"], (3, [1])),
    ("___ 붙을게요!", ["꼭"], (3, [2])),
    ("합격 ___ 여기 있어요!", ["엿"], (3, [3])),
]
L2_MATDA_NADA = [  # (sentence with ___, answer)
    ("이 옷이 잘 ___.", "맞아요"),
    ("어젯밤부터 열이 ___.", "나요"),
    ("우산이 없어서 비를 ___.", "맞았어요"),
    ("동생이 거짓말해서 화가 ___.", "났어요"),
    ("부엌에서 맛있는 냄새가 ___.", "나요"),
    ("어제 독감 주사를 ___.", "맞았어요"),
]
L2_MATDA_NADA_BANK = ["맞아요", "나요", "났어요", "맞았어요"]
L2_BODY = [  # (Korean, meaning) in Clare's order; right column is shuffled below
    ("귀가 얇다", "easily influenced"), ("발이 넓다", "well-connected"), ("입이 짧다", "a picky eater"),
    ("눈이 높다", "has high standards"), ("손이 빠르다", "works fast"), ("입이 무겁다", "keeps secrets"),
    ("눈치가 빠르다", "quick to read the room"), ("손발이 맞다", "works well together"),
]
L2_BODY_ORDER = [6, 2, 4, 1, 5, 0, 7, 3]  # fixed shuffle so every build is the same
L2_TIME = [  # (sentence with ___, English, answer)
    ("___ 도착했어요.", "I just arrived.", "방금"),
    ("___ 안 먹었어요.", "I haven't eaten yet.", "아직"),
    ("___ 갈게요.", "I'll be right there.", "금방"),
    ("___ 얘기해요.", "Let's talk later.", "나중에"),
    ("___ 점심시간이에요.", "It's already lunchtime.", "벌써"),
    ("___ 시작해요.", "It starts soon.", "곧"),
]
L2_TIME_BANK = ["방금", "아직", "금방", "나중에", "벌써", "곧"]
L2_SAY = [
    ("커피를 권하는 사람에게 정중하게 거절해보세요.", "아니요, 괜찮아요."),
    ("친구에게 시험 잘 보라고 말해보세요.", "시험 잘 봐!"),
    ("오늘 열이 나는 상황을 말해보세요.", "열이 나요."),
]

CSS2 = """
.dlg { margin-bottom:5mm; }
.dlg h3 { margin:0 0 2mm; font-size:12pt; }
.dlg h3 .sm { color:var(--muted); font-weight:400; font-size:10pt; margin-left:2mm; }
table.review td.sp { width:9mm; font-weight:700; color:var(--coral); }
table.review td .ex { display:block; margin-top:1mm; font-weight:400; font-size:9.4pt; color:var(--navy); }
table.review td.rr .ex { color:var(--muted); }
.note { background:var(--off); border-left:3px solid var(--coral); border-radius:0 2mm 2mm 0; padding:2.5mm 4mm; font-size:10pt; margin-top:2mm; }
.note b { color:var(--coral); }
.match { display:flex; justify-content:space-between; gap:10mm; margin-top:4mm; }
.match ol { list-style:none; margin:0; padding:0; flex:1; }
.match li { display:flex; align-items:center; gap:3mm; height:15mm; border-bottom:1px solid var(--line); font-size:12pt; }
.match .left li { font-weight:700; font-size:13pt; justify-content:space-between; }
.match .dot { width:3mm; height:3mm; border-radius:50%; background:var(--navy); flex:none; }
.match .key { color:var(--coral); font-weight:700; display:inline-block; width:7mm; }
.say .prompt { font-size:12.5pt; font-weight:700; margin:0 0 2mm; }
.say .hint { font-size:10pt; color:var(--muted); margin:0 0 3mm; }
.checks { display:flex; gap:4mm; align-items:center; font-size:9.5pt; color:var(--muted); }
.howto2 .box { padding:3.5mm 6mm; margin-bottom:2.5mm; }
.howto2 .toc li { padding:1.6mm 0; font-size:10.5pt; }
.checks span.box { width:5mm; height:5mm; border:1.5px solid var(--navy); border-radius:1mm; display:inline-block; }
"""


def page2(inner, n, total, cls=""):
    foot = "" if cls in ("cover", "end") else (
        f'<div class="foot"><span>Clare\'s Korean · Level 2 Workbook</span><span>{n} / {total}</span></div>')
    return f'<section class="page {cls}">{inner}{foot}</section>'


def blankify2(s):
    return e(s).replace("___", '<span class="blank">&nbsp;</span>')


def build_level2_html():
    d = load_level2()
    pages = []  # (cls, inner, contents label or None)

    pages.append(("cover", """
      <div><div class="brand">Stylish Korean Clare</div></div>
      <div><div class="bar"></div><h1>Clare's Korean<br>Workbook</h1>
        <span class="level">Level 2 · Mini Dialogues &amp; Real Expressions</span>
        <p class="sub">Real Korean for real conversations.<br>Listen, fill in the blanks, match, and speak.</p></div>
      <div class="bottom">Free workbook · """ + SITE + """</div>""", None))
    pages.append(("", "__HOWTO__", None))

    # Review: Mini Dialogues
    dl = ""
    for i, dg in enumerate(d["dialogues"], 1):
        rows = "".join(f'<tr><td class="sp">{e(l["speaker"])}</td><td class="kr">{e(l["kr"])}</td>'
                       f'<td class="rr">{e(l["rr"])}</td><td>{e(l["en"])}</td></tr>' for l in dg["lines"])
        note = ""
        if dg.get("note"):
            k, _, rest = dg["note"].partition(" = ")
            note = f'<div class="note"><b>{e(k)}</b> = {e(rest)}</div>'
        dl += (f'<div class="dlg"><h3>Dialogue {i} · {e(dg["emoji"])} {e(dg["title"])}'
               f'<span class="sm">{e(dg["en"])}</span></h3><table class="review">{rows}</table>{note}</div>')
    pages.append(("", '<span class="kicker">Review</span><h1>Mini Dialogues</h1>'
                  '<p class="lead">Listen to each line on the site (Mini Dialogues), then read it out loud.</p>' + dl,
                  ("Review", "Mini Dialogues")))

    def review(title, lead, cards, label):
        rows = "".join(
            f'<tr><td class="kr">{e(c.get("emoji", ""))} {e(c["kr"])}<span class="ex">{e(c["ex_kr"])}</span></td>'
            f'<td class="rr">{e(c["rr"])}<span class="ex">{e(c["ex_rr"])}</span></td>'
            f'<td>{e(c["en"])}<span class="ex">{e(c["ex_en"])}</span></td></tr>' for c in cards)
        return ("", f'<span class="kicker">Review</span><h1>{e(title)}</h1><p class="lead">{e(lead)}</p>'
                f'<table class="review"><tr><th>Korean</th><th>Romanization</th><th>English</th></tr>{rows}</table>',
                ("Review", label))
    pages.append(review("맞다 · 나다", "One word, many meanings. Each expression comes with an example sentence.",
                        d["matda"] + d["nada"], "맞다 · 나다"))
    pages.append(review("Body Expressions", "Korean expressions with body parts. Read each one out loud.",
                        d["body"], "Body Expressions"))
    pages.append(review("Time Words", "Words for earlier, later, soon, and already.", d["time"], "Time Words"))

    # Unit 1 · Listen & Choose
    qs = ""
    for i, (dn, q, opts, _) in enumerate(L2_LISTEN):
        o = "".join(f'<div class="opt"><span class="circle">{"abc"[j]}</span>{e(t)}</div>' for j, t in enumerate(opts))
        qs += (f'<div class="q quiz"><div class="num">{i + 1}</div><div class="body">'
               f'<span class="tag">Dialogue {dn}</span><p class="question">{e(q)}</p><div class="opts">{o}</div></div></div>')
    pages.append(("", '<span class="kicker">Unit 1 · Listen &amp; Choose</span><h2 style="margin-top:4mm">Listen and Choose</h2>'
                  '<p class="lead">Listen to the Mini Dialogues on the site, then circle a, b, or c.</p>' + qs,
                  ("Unit 1", f"Listen &amp; Choose ({len(L2_LISTEN)})")))

    # Unit 2 · Dictation
    qs = ""
    for i, (s, _, (dn, ln)) in enumerate(L2_DICTATION):
        en = " ".join(d["dialogues"][dn - 1]["lines"][k - 1]["en"] for k in ln)
        qs += (f'<div class="q"><div class="num">{i + 1}</div><div class="body"><span class="tag">Dialogue {dn}</span>'
               f'<p class="kr">{blankify2(s)}</p><p class="en">{e(en)}</p></div></div>')
    pages.append(("", '<span class="kicker">Unit 2 · Dictation</span><h2 style="margin-top:4mm">Listen and Write</h2>'
                  '<p class="lead">Play the dialogue audio on the site and write the missing words.</p>' + qs,
                  ("Unit 2", f"Dictation ({len(L2_DICTATION)})")))

    # Unit 3 · 맞다 / 나다
    ex_en = {c["ex_kr"].rstrip("."): c["ex_en"] for c in d["matda"] + d["nada"]}
    qs = ""
    for i, (s, a) in enumerate(L2_MATDA_NADA):
        en = ex_en.get(s.replace("___", a).rstrip("."), "")
        qs += (f'<div class="q"><div class="num">{i + 1}</div><div class="body">'
               f'<p class="kr">{blankify2(s)}</p><p class="en">{e(en)}</p></div></div>')
    bank = "".join(f"<span>{e(w)}</span>" for w in L2_MATDA_NADA_BANK)
    pages.append(("", '<span class="kicker">Unit 3 · Fill in the Blank</span><h2 style="margin-top:4mm">맞다 / 나다</h2>'
                  '<p class="lead">Choose the right word from the word bank. You can use a word more than once.</p>'
                  f'<div class="bank"><div class="t">Word Bank</div>{bank}</div>' + qs,
                  ("Unit 3", f"맞다 / 나다 Fill in the Blank ({len(L2_MATDA_NADA)})")))

    # Unit 4 · Body Expressions Match
    left = "".join(f'<li><span><span class="key">{i + 1}</span>{e(k)}</span><span class="dot"></span></li>'
                   for i, (k, _) in enumerate(L2_BODY))
    right = "".join(f'<li><span class="dot"></span><span class="key">{"abcdefgh"[j]}</span>{e(L2_BODY[idx][1])}</li>'
                    for j, idx in enumerate(L2_BODY_ORDER))
    pages.append(("", '<span class="kicker">Unit 4 · Match</span><h2 style="margin-top:4mm">Body Expressions</h2>'
                  '<p class="lead">Draw a line from each Korean expression to its meaning.</p>'
                  f'<div class="match"><ol class="left">{left}</ol><ol class="right">{right}</ol></div>',
                  ("Unit 4", f"Body Expressions Match ({len(L2_BODY)})")))

    # Unit 5 · Time Words
    qs = "".join(f'<div class="q"><div class="num">{i + 1}</div><div class="body">'
                 f'<p class="kr">{blankify2(s)}</p><p class="en">{e(en)}</p></div></div>'
                 for i, (s, en, _) in enumerate(L2_TIME))
    bank = "".join(f"<span>{e(w)}</span>" for w in L2_TIME_BANK)
    pages.append(("", '<span class="kicker">Unit 5 · Fill in the Blank</span><h2 style="margin-top:4mm">Time Words</h2>'
                  '<p class="lead">Choose the right time word from the word bank.</p>'
                  f'<div class="bank"><div class="t">Word Bank</div>{bank}</div>' + qs,
                  ("Unit 5", f"Time Words ({len(L2_TIME)})")))

    # Unit 6 · Say It!
    qs = "".join(f'<div class="q say"><div class="num">{i + 1}</div><div class="body">'
                 f'<p class="prompt">{e(p)}</p><p class="hint">({e(h)})</p>'
                 '<div class="checks">I said it out loud: <span class="box"></span><span class="box"></span>'
                 '<span class="box"></span></div></div></div>' for i, (p, h) in enumerate(L2_SAY))
    pages.append(("", '<span class="kicker">Unit 6 · Say It!</span><h2 style="margin-top:4mm">Speaking Challenge</h2>'
                  '<p class="lead">No answer key here — say each one out loud three times. Check a box each time.</p>' + qs,
                  ("Unit 6", "Say It!")))

    # Answer key (Units 1–5)
    a1 = "".join(f'<li><b>{"abc"[k]}</b> <span class="sm">— {e(o[k])}</span></li>' for _, _, o, k in L2_LISTEN)
    a2 = "".join(f'<li><b>{e(" / ".join(a))}</b> <span class="sm">— {e(s.replace("___", "{}").format(*a))}</span></li>'
                 for s, a, _ in L2_DICTATION)
    a3 = "".join(f'<li><b>{e(a)}</b> <span class="sm">— {e(s.replace("___", a))}</span></li>' for s, a in L2_MATDA_NADA)
    pos = {idx: j for j, idx in enumerate(L2_BODY_ORDER)}
    a4 = "".join(f'<li><b>{"abcdefgh"[pos[i]]}</b> <span class="sm">— {e(k)} = {e(m)}</span></li>'
                 for i, (k, m) in enumerate(L2_BODY))
    a5 = "".join(f'<li><b>{e(a)}</b> <span class="sm">— {e(s.replace("___", a))}</span></li>' for s, _, a in L2_TIME)
    pages.append(("", '<span class="kicker">Answers</span><h1>Answer Key</h1>'
                  '<p class="lead">Check your answers. Then listen on the site and repeat after Clare.</p>'
                  f'<div class="answers"><div class="grp"><h3>Unit 1 · Listen &amp; Choose</h3><ol>{a1}</ol></div>'
                  f'<div class="grp"><h3>Unit 2 · Dictation</h3><ol>{a2}</ol></div>'
                  f'<div class="grp"><h3>Unit 3 · 맞다 / 나다</h3><ol>{a3}</ol></div>'
                  f'<div class="grp"><h3>Unit 4 · Body Expressions</h3><ol>{a4}</ol></div>'
                  f'<div class="grp"><h3>Unit 5 · Time Words</h3><ol>{a5}</ol></div></div>',
                  ("Answers", "Answer Key")))

    pages.append(("end", f"""
      <span class="kicker">Great Job!</span><h1>잘했어요!</h1>
      <p>You finished the Level 2 workbook. Keep practicing with Clare's Mini Dialogues, flashcards,
      noun + verb pairs, and the listening quiz on the site.</p>
      <span class="url">{SITE}</span>""", None))

    toc = "".join(f'<li><span><b>{k}</b>{v}</span><span>{n}</span></li>'
                  for n, (_, _, lab) in enumerate(pages, 1) if lab for k, v in [lab])
    howto = f"""<div class="howto2">
      <span class="kicker">Start Here</span><h1>How to Use This Workbook</h1>
      <p class="lead">Every phrase in this workbook comes from the Mini Dialogues, Learn Them as Pairs, Body Expressions,
      and Time Words cards on the Clare's Korean site. Listen to Clare's audio there, then practice here.</p>
      <div class="box"><h3>1. Review</h3><p>Read the dialogues and expressions first. Say each one out loud.</p></div>
      <div class="box"><h3>2. Listen &amp; Write</h3><p>Play the Mini Dialogues on the site to answer Units 1 and 2.</p></div>
      <div class="box"><h3>3. Practice</h3><p>Fill in the blanks, match the expressions, and check your answers at the end.</p></div>
      <div class="box"><h3>4. Say It!</h3><p>Finish with a speaking challenge. Say each answer out loud.</p></div>
      <h2 style="margin-top:5mm">Contents</h2><ul class="toc">{toc}</ul></div>"""
    pages[1] = ("", howto, None)

    total = len(pages)
    body = "".join(page2(inner, i + 1, total, cls) for i, (cls, inner, _) in enumerate(pages))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="google" content="notranslate">'
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">'
            f'<style>{CSS}{CSS2}</style></head><body translate="no">{body}</body></html>'), total


def main_level2():
    doc, total = build_level2_html()
    OUT2.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(doc, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        over = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((s, i) => {
            const foot = s.querySelector('.foot'); const limit = foot ? foot.offsetTop : s.clientHeight;
            const kids = [...s.children].filter(c => c !== foot);
            const bottom = Math.max(...kids.map(c => c.offsetTop + c.offsetHeight));
            return bottom > limit ? i + 1 : 0; }).filter(Boolean)""")
        if over:
            raise SystemExit(f"Level 2: content overflows on page(s) {over}. Nothing written.")
        pg.pdf(path=str(OUT2), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    print(f"Wrote {OUT2.relative_to(ROOT)} ({total} pages)")


if __name__ == "__main__":
    import sys
    if "--level" in sys.argv and sys.argv[sys.argv.index("--level") + 1] == "2":
        main_level2()
    else:
        main()
