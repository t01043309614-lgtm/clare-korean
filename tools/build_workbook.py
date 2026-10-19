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
    everyday = parse_entries(every)
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
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>{body}</body></html>'), total


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


if __name__ == "__main__":
    main()
