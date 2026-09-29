"""Generate the full-page dark dashboard SVG for the profile README. Run: python generate_dashboard.py"""
import base64
import datetime
import html
import json
import pathlib
import random
import re
import subprocess
import urllib.request

OWNER = "ashis2489"
LC_USER = "2301301008"
LINKEDIN = "ashish-vibhor-506a1a28a"
OUT = pathlib.Path("assets")
PAGE_SVG = OUT / "page.svg"
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Cascadia Code', 'Fira Code', Consolas, monospace"
SCRIPT = "'Segoe Script', 'Bradley Hand', cursive"

PAGE = "#0a0e15"
CARD = "#111824"
CARD2 = "#0d141f"
BORDER = "#263140"
H = "#f0f6fc"
T = "#c9d1d9"
MU = "#8b949e"
ACC = "#58a6ff"
CY = "#22d3ee"
GREEN = "#3fb950"
LC = "#ffa116"

KW, FN, KEY, STR, PUN = "#ff7b72", "#79c0ff", "#d2a8ff", "#a5d6ff", "#c9d1d9"

W = 1000
M = 22
CW = W - 2 * M


def gh(*args, tries=4):
    import time
    for attempt in range(tries):
        out = subprocess.run(["gh", "api", *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        if out.returncode == 0:
            return json.loads(out.stdout)
        if attempt == tries - 1:
            raise RuntimeError(f"gh api failed: {out.stderr[:300]}")
        time.sleep(20 * (attempt + 1))


def fetch(url, data=None, headers=None):
    hdr = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    hdr.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdr)
    return urllib.request.urlopen(req, timeout=30).read()


def esc(s):
    return html.escape(str(s), quote=True)


def text(x, y, s, size=13, fill=T, weight="400", anchor="start", family=None,
         style="normal", opacity=None, transform=None):
    extra = ""
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    if transform:
        extra += f' transform="{transform}"'
    return (f'<text x="{x}" y="{y}" font-family="{family or FONT}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" '
            f'font-style="{style}"{extra}>{esc(s)}</text>')


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1, opacity=None):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}"{st}{op}/>')


def wrap(s, max_chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(x, y, w, h, rx=14, fill=CARD):
    return rect(x, y, w, h, fill, rx=rx, stroke=BORDER, sw=1.2)


def svg_doc(w, h, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">\n<style>{css}</style>\n{body}\n</svg>\n')


def icon_img(b64, x, y, size):
    return (f'<image href="data:image/svg+xml;base64,{b64}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{size}" height="{size}"/>')


def png_img(b64, x, y, w, h, rx=8, cid="thumb"):
    return (f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" rx="{rx}"/></clipPath>'
            f'<image href="data:image/png;base64,{b64}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" clip-path="url(#{cid})" '
            f'preserveAspectRatio="xMidYMid slice"/>')


def pill(x, y, w, h, label, dot=False, size=11, fill=CARD2, stroke=BORDER,
         tcolor=T, weight="500"):
    body = rect(x, y, w, h, fill, rx=h / 2, stroke=stroke)
    gap = 14 if dot else 0
    body += text(x + w / 2 + gap / 2, y + h / 2 + size * 0.36, label, size=size,
                 fill=tcolor, anchor="middle", weight=weight)
    if dot:
        body += (f'<circle cx="{x + 16}" cy="{y + h / 2}" r="5" fill="{GREEN}" '
                 f'style="animation: pulse 1.8s ease-in-out infinite"/>')
    return body


def heading(y, label, emoji=None, sub=None):
    parts = []
    x = M
    if emoji:
        parts.append(text(x, y, emoji, size=17))
        x += 30
    parts.append(text(x, y, label, size=20, fill=H, weight="800"))
    lx = x + len(label) * 11 + 12
    parts.append(rect(lx, y - 8, 26, 3, ACC, rx=1.5))
    if sub:
        parts.append(text(M, y + 20, sub, size=11.5, fill=MU))
    return "\n".join(parts)


def hexpath(cx, cy, r):
    dx = r * 0.866
    pts = [(cx, cy - r), (cx + dx, cy - r / 2), (cx + dx, cy + r / 2),
           (cx, cy + r), (cx - dx, cy + r / 2), (cx - dx, cy - r / 2)]
    return "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"


def scene_defs():
    return ('<defs>'
            '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#141132"/>'
            '<stop offset="0.45" stop-color="#3a2a66"/>'
            '<stop offset="0.72" stop-color="#7c4680"/>'
            '<stop offset="0.9" stop-color="#c2657e"/>'
            '<stop offset="1" stop-color="#e29168"/></linearGradient>'
            '<linearGradient id="heroG" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#a78bfa"/>'
            '<stop offset="0.55" stop-color="#7c9cff"/>'
            '<stop offset="1" stop-color="#22d3ee"/></linearGradient>'
            '<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#0a0e15" stop-opacity="0.93"/>'
            '<stop offset="0.6" stop-color="#0a0e15" stop-opacity="0.35"/>'
            '<stop offset="1" stop-color="#0a0e15" stop-opacity="0.05"/></linearGradient>'
            '<linearGradient id="btn" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#7c5cff"/>'
            '<stop offset="1" stop-color="#4d8dff"/></linearGradient>'
            '<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#a78bfa"/>'
            '<stop offset="1" stop-color="#22d3ee"/></linearGradient>'
            '<linearGradient id="qsky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#1b1638"/>'
            '<stop offset="1" stop-color="#4b2f6e"/></linearGradient>'
            '</defs>')


def city_scape(y_top, y_base, seed, fill, win="#ffd47e", wmin=26, wmax=70,
               hmin=30, hmax=110):
    rnd = random.Random(seed)
    parts = []
    x = -10
    while x < W + 10:
        bw = rnd.uniform(wmin, wmax)
        bh = rnd.uniform(hmin, hmax)
        top = y_base - bh
        if top < y_top:
            top = y_top
        parts.append(rect(x, top, bw, y_base - top, fill))
        wy = top + 8
        while wy < y_base - 12:
            wx = x + 5
            while wx < x + bw - 8:
                if rnd.random() < 0.35:
                    parts.append(rect(wx, wy, 4, 5, win,
                                      opacity=f"{rnd.uniform(0.25, 0.9):.2f}"))
                wx += 9
            wy += 13
        x += bw + rnd.uniform(2, 8)
    return "".join(parts)


def build_nav(gh_icon, li_box):
    hgt = 54
    parts = [rect(0, 0, W, hgt, "#0b111c")]
    parts.append(rect(M, 12, 30, 30, "#161e2b", rx=8, stroke=BORDER))
    parts.append(text(M + 15, 33, ">_", size=13, fill=CY, weight="800",
                      anchor="middle", family=MONO))
    parts.append(text(M + 40, 33, "ASHISH", size=15, fill=H, weight="800"))
    tabs = ["Home", "About", "Projects", "Skills", "Stats", "Achievements", "Contact"]
    x = M + 130
    for i, t in enumerate(tabs):
        active = i == 0
        parts.append(text(x, 33, t, size=12.5, fill=H if active else MU,
                          weight="700" if active else "500"))
        tw = len(t) * 6.8
        if active:
            parts.append(rect(x, 50, tw, 3, CY, rx=1.5))
        x += tw + 20
    sx = W - M - 262
    parts.append(rect(sx, 12, 160, 30, "#0d141f", rx=8, stroke=BORDER))
    parts.append(text(sx + 14, 31, "Search repositories...", size=11.5, fill=MU))
    parts.append(rect(sx + 170, 12, 30, 30, "#0d141f", rx=8, stroke=BORDER))
    parts.append(icon_img(gh_icon, sx + 177, 19, 16))
    parts.append(rect(sx + 206, 12, 30, 30, "#0d141f", rx=8, stroke=BORDER))
    parts.append(li_box(sx + 213, 19))
    for i, c in enumerate([LC, ACC, "#a78bfa"]):
        parts.append(f'<circle cx="{sx + 250}" cy="{20 + i * 7}" r="3" fill="{c}"/>')
    parts.append(f'<line x1="0" y1="{hgt}" x2="{W}" y2="{hgt}" stroke="{BORDER}"/>')
    return hgt, "\n".join(parts)


def build_hero(icons):
    hgt = 330
    y0 = 0
    parts = [rect(0, y0, W, hgt, PAGE)]
    parts.append(scene_defs())
    parts.append(rect(0, y0, W, hgt, "url(#sky)"))
    rnd = random.Random(7)
    for _ in range(55):
        parts.append(f'<circle cx="{rnd.uniform(0, W):.1f}" '
                     f'cy="{rnd.uniform(y0 + 4, y0 + 120):.1f}" '
                     f'r="{rnd.uniform(0.4, 1.3):.1f}" fill="#dbe4ff" '
                     f'opacity="{rnd.uniform(0.15, 0.7):.2f}"/>')
    parts.append(city_scape(y0 + 120, y0 + 252, 21, "#241c4a", hmin=40, hmax=110))
    parts.append(city_scape(y0 + 170, y0 + 262, 5, "#171136", hmin=34, hmax=92))
    parts.append(rect(0, y0 + 258, W, hgt - 204, "#0c0918"))
    parts.append(rect(540, y0 + 258, 410, 10, "#1b1630"))
    parts.append(rect(556, y0 + 268, 8, 52, "#15112a"))
    parts.append(rect(916, y0 + 268, 8, 52, "#15112a"))
    for mx, my, mw, mh, seed in [(560, y0 + 178, 160, 78, 3), (734, y0 + 172, 176, 86, 9)]:
        parts.append(rect(mx, my, mw, mh, "#0e1526", rx=6, stroke="#2b3a55", sw=2))
        parts.append(rect(mx + 8, my + 8, mw - 16, mh - 16, "#111f3a", rx=3))
        rr = random.Random(seed)
        ly = my + 16
        while ly < my + mh - 18:
            lw = rr.uniform(30, mw - 40)
            col = [ACC, "#a78bfa", GREEN, "#f778ba", STR][rr.randrange(5)]
            parts.append(rect(mx + 16, ly, lw, 4, col, rx=2,
                              opacity=f"{rr.uniform(0.5, 0.95):.2f}"))
            ly += 11
    parts.append(rect(612, y0 + 268, 120, 9, "#241d38", rx=4))
    parts.append(rect(862, y0 + 196, 54, 72, "#120e22", rx=14))
    parts.append(f'<ellipse cx="856" cy="{y0 + 250}" rx="36" ry="28" fill="#0e0b1c"/>')
    parts.append(f'<circle cx="846" cy="{y0 + 210}" r="19" fill="#0e0b1c"/>')
    parts.append(f'<path d="M 830 {y0 + 200} q 16 -14 32 -2 q -8 -8 -18 -6 '
                 f'q -8 2 -14 8 Z" fill="#070510"/>')
    parts.append(rect(0, y0, W, hgt, "url(#fade)"))
    for i, line in enumerate(["Code.", "Create.", "Contribute.", "Repeat."]):
        ry = y0 + 66 + i * 27
        parts.append(text(974, ry, line, size=21, fill="#e8ddf7", family=SCRIPT,
                          anchor="end", transform=f"rotate(-8 974 {ry})"))
    cx0, cy0 = 716, y0 + 232
    parts.append(rect(cx0, cy0, 248, 84, "#0b101c", rx=10, stroke=BORDER))
    parts.append(rect(cx0 + 12, cy0 + 12, 7, 7, "#ff5f56", rx=3.5))
    parts.append(rect(cx0 + 24, cy0 + 12, 7, 7, "#ffbd2e", rx=3.5))
    parts.append(rect(cx0 + 36, cy0 + 12, 7, 7, "#27c93f", rx=3.5))
    code = [([("while ", KW),("(learning)", FN),(" {", PUN)]),
            ([("  keepBuilding", FN),("();", PUN)]),
            ([("  keepGrowing", FN),("();", PUN)]),
            ([("  makeItBetter", FN),("();", PUN)]),
            ([("}", PUN)])]
    for i, ln in enumerate(code):
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in ln)
        parts.append(f'<text x="{cx0 + 16}" y="{cy0 + 40 + i * 13}" '
                     f'font-family="{MONO}" font-size="10.5">{spans}</text>')
    parts.append(text(M + 4, y0 + 62, "Hey, I'm", size=16, fill="#d8e2f2",
                      family=MONO, weight="600"))
    parts.append(text(M + 2, y0 + 134, "ASHISH", size=66, fill="url(#heroG)",
                      weight="800"))
    parts.append(f'<text x="{M + 4}" y="{y0 + 170}" font-family="{FONT}" font-size="18" '
                 f'font-weight="700" fill="{H}">Full-Stack Developer '
                 f'<tspan fill="{CY}">| Software Engineer</tspan></text>')
    parts.append(text(M + 4, y0 + 200,
                      "I build scalable web applications, solve real-world problems,",
                      size=13, fill="#c5cede"))
    parts.append(text(M + 4, y0 + 220,
                      "and turn ideas into meaningful digital products.",
                      size=13, fill="#c5cede"))
    bx = M + 4
    parts.append(rect(bx, y0 + 246, 178, 44, "url(#btn)", rx=10))
    parts.append(text(bx + 89, y0 + 274, "Explore My Work →", size=14, fill="#ffffff",
                      weight="700", anchor="middle"))
    bx += 190
    parts.append(rect(bx, y0 + 246, 148, 44, "#101725", rx=10, stroke="#3a465c"))
    parts.append(icon_img(icons["github"], bx + 16, y0 + 257, 22))
    parts.append(text(bx + 46, y0 + 274, "View GitHub", size=13.5, fill=T,
                      weight="600"))
    bx += 160
    parts.append(rect(bx, y0 + 246, 152, 44, "#101725", rx=10, stroke="#3a465c"))
    parts.append(text(bx + 76, y0 + 274, "✈  Let's Connect", size=13.5, fill=T,
                      weight="600", anchor="middle"))
    return hgt, "\n".join(parts)


def build_strip():
    hgt = 76
    tiles = [
        ("cal", "389", "GitHub Contributions"),
        ("repo", "27", "Public Repositories"),
        ("box", "4", "Featured Projects"),
        ("lc", "182", "LeetCode Solved"),
    ]
    parts = [rect(0, 0, W, hgt, "#0c1119"),
             f'<line x1="0" y1="0" x2="{W}" y2="0" stroke="{BORDER}"/>',
             f'<line x1="0" y1="{hgt - 1}" x2="{W}" y2="{hgt - 1}" stroke="{BORDER}"/>']
    cw = CW / 4
    for i, (kind, value, label) in enumerate(tiles):
        x = M + i * cw
        if i:
            parts.append(f'<line x1="{x:.0f}" y1="16" x2="{x:.0f}" y2="{hgt - 16}" '
                         f'stroke="{BORDER}"/>')
        accent = [ACC, "#a78bfa", CY, LC][i]
        parts.append(rect(x + 26, 18, 40, 40, "#161e2b", rx=10, stroke=BORDER))
        gx, gy = x + 46, 38
        if kind == "cal":
            parts.append(rect(gx - 9, gy - 8, 18, 16, "none", rx=3, stroke=accent, sw=2))
            parts.append(rect(gx - 9, gy - 12, 18, 6, "none", rx=2, stroke=accent, sw=2))
        elif kind == "repo":
            parts.append(rect(gx - 9, gy - 8, 18, 16, "none", rx=3, stroke=accent, sw=2))
            parts.append(f'<circle cx="{gx - 3}" cy="{gy}" r="2.5" fill="{accent}"/>')
        elif kind == "box":
            parts.append(f'<path d="M {gx} {gy - 10} L {gx + 10} {gy - 4} L {gx + 10} {gy + 6} '
                         f'L {gx} {gy + 12} L {gx - 10} {gy + 6} L {gx - 10} {gy - 4} Z" '
                         f'fill="none" stroke="{accent}" stroke-width="2"/>')
        else:
            parts.append(f'<path d="M {gx + 3} {gy - 8} L {gx - 5} {gy} L {gx + 3} {gy + 8}" '
                         f'fill="none" stroke="{accent}" stroke-width="2" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>'
                         f'<path d="M {gx - 3} {gy - 8} L {gx + 5} {gy} L {gx - 3} {gy + 8}" '
                         f'fill="none" stroke="{accent}" stroke-width="2" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>')
        parts.append(text(x + 80, 40, value, size=20, fill=H, weight="800"))
        parts.append(text(x + 80, 58, label, size=10.5, fill=MU))
    return hgt, "\n".join(parts)


def build_about(avatar_b64):
    hgt = 250
    parts = [heading(26, "About Me", emoji="👤")]
    lw = 560
    y = 48
    parts.append(card(M, y, lw, 190, rx=14))
    parts.append(f'<clipPath id="avclip"><circle cx="{M + 90}" cy="{y + 80}" r="50"/>'
                 f'</clipPath>')
    parts.append(f'<circle cx="{M + 90}" cy="{y + 80}" r="54" fill="none" '
                 f'stroke="url(#ring)" stroke-width="3"/>')
    parts.append(f'<image href="data:image/png;base64,{avatar_b64}" x="{M + 38}" '
                 f'y="{y + 28}" width="104" height="104" clip-path="url(#avclip)" '
                 f'preserveAspectRatio="xMidYMid slice"/>')
    parts.append(pill(M + 50, y + 142, 82, 24, "Online", dot=True, size=10.5,
                      fill="#0e1c14", stroke="#1e4d2f", tcolor="#7ee2a8"))
    para = ("I'm a full-stack web developer from India, passionate about building "
            "impactful products, solving real-world problems and continuous learning. "
            "I love full-stack development, exploring new technologies and turning "
            "ideas into scalable web applications.")
    py = y + 42
    for line in wrap(para, 56):
        parts.append(text(M + 170, py, line, size=12.5, fill=T))
        py += 18
    chx = M + 170
    for label, gl in [("🇮🇳 India", 62), ("⚡ Open Source", 92),
                      ("● Open to Opportunities", 148)]:
        parts.append(pill(chx, y + 148, gl, 26, label, size=10.5))
        chx += gl + 8
    rx0 = M + lw + 16
    rw = CW - lw - 16
    parts.append(card(rx0, y, rw, 190, rx=14))
    parts.append(rect(rx0 + 1, y + 1, rw - 2, 34, "#0b111c", rx=13))
    parts.append(f'<path d="M {rx0 + 1} {y + 34} L {rx0 + rw - 1} {y + 34}" '
                 f'stroke="{BORDER}"/>')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{rx0 + 18 + i * 16}" cy="{y + 18}" r="5" fill="{c}"/>')
    tx = rx0 + 84
    for i, t in enumerate(["About", "Education", "Interests"]):
        tw = len(t) * 6.6
        parts.append(text(tx, y + 22, t, size=11,
                          fill=H if i == 0 else MU,
                          weight="700" if i == 0 else "500"))
        if i == 0:
            parts.append(rect(tx, y + 31, tw, 3, ACC, rx=1.5))
        tx += tw + 18
    lines = [
        [("const ", KW), ("ashish", FN), (" = {", PUN)],
        [("  role", KEY), (": ", PUN), ('"Full-Stack Developer"', STR), (",", PUN)],
        [("  location", KEY), (": ", PUN), ('"India"', STR), (",", PUN)],
        [("  leetcode", KEY), (": ", PUN), ('"182 problems solved"', STR), (",", PUN)],
        [("  interests", KEY), (": [", PUN), ('"Web Dev", "UI/UX"', STR), ("],", PUN)],
        [("  currently", KEY), (": ", PUN), ('"Building real projects"', STR), (",", PUN)],
        [("  goal", KEY), (": ", PUN), ('"Create impactful products"', STR), (",", PUN)],
        [("};", PUN)],
    ]
    for i, ln in enumerate(lines):
        ly = y + 56 + i * 16
        parts.append(text(rx0 + 18, ly, str(i + 1), size=10, fill="#4b5563",
                          anchor="end", family=MONO))
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in ln)
        parts.append(f'<text x="{rx0 + 32}" y="{ly}" font-family="{MONO}" '
                     f'font-size="10.5">{spans}</text>')
    return hgt, "\n".join(parts)


def build_tech(icons):
    hgt = 162
    parts = [heading(26, "Tech Stack", emoji="</>",
                     sub="Tools and technologies I work with")]
    filters = ["All", "Languages", "Frontend", "Backend", "Database", "Tools", "Others"]
    fx = W - M
    for t in reversed(filters):
        w = len(t) * 6.6 + 26
        fx -= w + 8
        active = t == "All"
        parts.append(pill(fx, 10, w, 26, t, size=11,
                          fill="#1d2b4d" if active else CARD2,
                          stroke="#2f4f8f" if active else BORDER,
                          tcolor="#9ecbff" if active else MU,
                          weight="700" if active else "500"))
    items = [("cplusplus", "C++"), ("javascript", "JavaScript"),
             ("typescript", "TypeScript"), ("react", "React"),
             ("nextdotjs", "Next.js"), ("nodedotjs", "Node.js"),
             ("express", "Express"), ("mongodb", "MongoDB"),
             ("postgresql", "Postgres"), ("prisma", "Prisma"),
             ("docker", "Docker"), ("git", "Git"),
             ("tailwindcss", "Tailwind"), ("vercel", "Vercel")]
    n = len(items)
    gap = 5
    cw = (CW - (n - 1) * gap) / n
    y = 62
    for i, (slug, label) in enumerate(items):
        x = M + i * (cw + gap)
        parts.append(card(x, y, cw, 84, rx=11, fill=CARD2))
        parts.append(rect(x + cw / 2 - 17, y + 14, 34, 34, "#161e2b", rx=9,
                          stroke=BORDER))
        if slug in icons:
            parts.append(icon_img(icons[slug], x + cw / 2 - 11, y + 20, 22))
        parts.append(text(x + cw / 2, y + 68, label, size=9.5, fill=MU,
                          anchor="middle"))
    return hgt, "\n".join(parts)


def build_projects(projects, gh_icon, badge_imgs):
    hgt = 582
    parts = [heading(26, "Featured Projects", emoji="📦",
                     sub="A showcase of my recent work, personal projects, and "
                         "real-world applications.")]
    bw = 150
    parts.append(pill(W - M - bw, 8, bw, 32, "View All Projects →", size=12,
                      fill=CARD2, tcolor=ACC, weight="700"))
    cw = (CW - 2 * 14) / 3
    ch = 244
    cells = [(i, p) for i, p in enumerate(projects)]
    for i, p in cells:
        col, row = i % 3, i // 3
        x = M + col * (cw + 14)
        y = 62 + row * (ch + 14)
        parts.append(card(x, y, cw, ch, rx=14))
        parts.append(png_img(p["thumb"], x + 12, y + 12, cw - 24, 96, rx=8,
                             cid=f"th{i}"))
        parts.append(rect(x + 14, y + 122, 26, 26, p["accent"], rx=7))
        parts.append(text(x + 27, y + 140, p["letter"], size=13, fill="#ffffff",
                          weight="800", anchor="middle"))
        parts.append(text(x + 48, y + 140, p["title"], size=14, fill=H, weight="800"))
        dy = y + 164
        for line in wrap(p["desc"], 47)[:2]:
            parts.append(text(x + 14, dy, line, size=11, fill=MU))
            dy += 15
        tx = x + 14
        for tag in p["tags"]:
            tw = len(tag) * 5.6 + 16
            parts.append(rect(tx, y + 196, tw, 20, "#161e2b", rx=10, stroke=BORDER))
            parts.append(text(tx + tw / 2, y + 210, tag, size=9.5, fill=T,
                              anchor="middle"))
            tx += tw + 5
        parts.append(f'<line x1="{x + 14}" y1="{y + 224}" x2="{x + cw - 14}" '
                     f'y2="{y + 224}" stroke="{BORDER}"/>')
        parts.append(text(x + 14, y + 238, "Repo →", size=11.5, fill=ACC,
                          weight="700"))
        parts.append(text(x + cw - 14, y + 238, "‹/› Code", size=11, fill=MU,
                          anchor="end"))
    y2 = 62 + ch + 14
    x3 = M + 2 * (cw + 14)
    parts.append(card(x3, y2, cw, ch, rx=14))
    for j, (bimg, blabel) in enumerate(badge_imgs):
        hx = x3 + 58 + j * ((cw - 80) / 3)
        parts.append(f'<path d="{hexpath(hx, y2 + 56, 40)}" fill="#161e2b" '
                     f'stroke="url(#ring)" stroke-width="2.5"/>')
        parts.append(f'<image href="data:image/png;base64,{bimg}" x="{hx - 27}" '
                     f'y="{y2 + 29}" width="54" height="54"/>')
        parts.append(text(hx, y2 + 112, blabel, size=9.5, fill=MU, anchor="middle"))
    parts.append(rect(x3 + 14, y2 + 126, 26, 26, "#8B5CF6", rx=7))
    parts.append(text(x3 + 27, y2 + 144, "B", size=13, fill="#ffffff", weight="800",
                      anchor="middle"))
    parts.append(text(x3 + 48, y2 + 144, "GitHub Badges", size=14, fill=H,
                      weight="800"))
    parts.append(text(x3 + 14, y2 + 168, "My GitHub achievements and collaboration "
                                         "journey.", size=11, fill=MU))
    tx = x3 + 14
    for tag in ["Git", "GitHub", "Open Source"]:
        tw = len(tag) * 5.6 + 16
        parts.append(rect(tx, y2 + 196, tw, 20, "#161e2b", rx=10, stroke=BORDER))
        parts.append(text(tx + tw / 2, y2 + 210, tag, size=9.5, fill=T,
                          anchor="middle"))
        tx += tw + 5
    parts.append(f'<line x1="{x3 + 14}" y1="{y2 + 224}" x2="{x3 + cw - 14}" '
                 f'y2="{y2 + 224}" stroke="{BORDER}"/>')
    parts.append(text(x3 + 14, y2 + 238, "View Repo →", size=11.5, fill=ACC,
                      weight="700"))
    parts.append(text(x3 + cw - 14, y2 + 238, "‹/› Code", size=11, fill=MU,
                      anchor="end"))
    xc = M + cw + 14
    parts.append(card(xc, y2, cw, ch, rx=14, fill=CARD2))
    parts.append(icon_img(gh_icon, xc + cw / 2 - 34, y2 + 44, 68))
    parts.append(text(xc + cw / 2, y2 + 146, "27 Public Repositories", size=17,
                      fill=H, weight="800", anchor="middle"))
    for j, line in enumerate(wrap("Browse everything I've built — apps, tools and "
                                  "experiments.", 46)[:2]):
        parts.append(text(xc + cw / 2, y2 + 170 + j * 15, line, size=11,
                          fill=MU, anchor="middle"))
    parts.append(pill(xc + cw / 2 - 92, y2 + 192, 184, 36, "View All Projects →",
                      size=12.5, fill="#1d2b4d", stroke="#2f4f8f", tcolor="#9ecbff",
                      weight="700"))
    return hgt, "\n".join(parts)


def heatmap_parts(x0, y0, contrib, cols, cell, gap, label=True):
    days = [d for week in contrib["weeks"] for d in week["contributionDays"]]
    days = days[-cols * 7:]
    by_date = {d["date"]: d["contributionCount"] for d in days}
    d0 = datetime.date.fromisoformat(days[0]["date"])
    levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    parts, last_label = [], -99
    for c in range(cols):
        for r in range(7):
            dt = d0 + datetime.timedelta(days=c * 7 + r)
            if dt.isoformat() not in by_date:
                continue
            cnt = by_date[dt.isoformat()]
            lvl = 0 if cnt == 0 else 1 if cnt <= 1 else 2 if cnt <= 3 else 3 if cnt <= 5 else 4
            parts.append(rect(x0 + c * (cell + gap), y0 + r * (cell + gap), cell, cell,
                              levels[lvl], rx=2))
        wd = d0 + datetime.timedelta(days=c * 7)
        if label and (c == 0 or wd.day <= 7) and c - last_label >= 6:
            last_label = c
            parts.append(text(x0 + c * (cell + gap), y0 - 8, wd.strftime("%b"), size=9,
                              fill=MU, anchor="middle"))
    if label:
        for i, lab in [(0, "Mon"), (2, "Wed"), (4, "Fri")]:
            parts.append(text(x0 - 8, y0 + i * (cell + gap) + 7, lab, size=8.5, fill=MU,
                              anchor="end"))
    return parts


def build_stats(contrib, stats, lc, icons):
    hgt = 278
    parts = [heading(26, "GitHub & LeetCode Stats", emoji="📊",
                     sub="My coding journey and contributions over time.")]
    for i, t in enumerate(["7D", "1M", "6M", "1Y", "All"]):
        w = 34
        x = W - M - (5 - i) * (w + 6)
        active = t == "1Y"
        parts.append(pill(x, 8, w, 26, t, size=11,
                          fill="#1d2b4d" if active else CARD2,
                          stroke="#2f4f8f" if active else BORDER,
                          tcolor="#9ecbff" if active else MU,
                          weight="700" if active else "500"))
    y = 62
    lw = 500
    parts.append(card(M, y, lw, 200, rx=14))
    parts.append(rect(M + 16, y + 14, 26, 26, "#161e2b", rx=7, stroke=BORDER))
    parts.append(text(M + 29, y + 32, "▦", size=13, fill=GREEN, anchor="middle"))
    parts.append(text(M + 52, y + 32, "GitHub Contributions", size=13.5, fill=H,
                      weight="800"))
    cell, gap = 7.5, 2
    avail = lw - 54 - 14
    cols = int(avail // (cell + gap))
    parts.extend(heatmap_parts(M + 54, y + 56, contrib, cols, cell, gap))
    parts.append(text(M + 16, y + 184, f"Total Contributions: {contrib['totalContributions']}",
                      size=11, fill=MU))
    lx = M + lw - 150
    parts.append(text(lx, y + 184, "Less", size=9.5, fill=MU))
    for i in range(5):
        lv = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"][i]
        parts.append(rect(lx + 30 + i * 14, y + 175, 10, 10, lv, rx=2))
    parts.append(text(lx + 106, y + 184, "More", size=9.5, fill=MU))
    tx = M + lw + 16
    tw = 176
    parts.append(card(tx, y, tw, 200, rx=14))
    rows = [("commits", str(stats["commits"]), "Total Commits"),
            ("prs", str(stats["prs"]), "Pull Requests"),
            ("issues", str(stats["issues"]), "Issues Resolved")]
    for i, (kind, value, label) in enumerate(rows):
        ry = y + 18 + i * 62
        parts.append(rect(tx + 14, ry, 34, 34, "#161e2b", rx=9, stroke=BORDER))
        gx, gy = tx + 31, ry + 17
        accent = [ACC, "#a78bfa", CY][i]
        if kind == "commits":
            parts.append(f'<circle cx="{gx}" cy="{gy}" r="5" fill="{accent}"/>'
                         f'<path d="M {gx} {gy + 5} L {gx} {gy + 10}" stroke="{accent}" '
                         f'stroke-width="2"/>')
        elif kind == "prs":
            parts.append(f'<circle cx="{gx - 3}" cy="{gy - 6}" r="3" fill="none" '
                         f'stroke="{accent}" stroke-width="2"/>'
                         f'<circle cx="{gx - 3}" cy="{gy + 7}" r="3" fill="none" '
                         f'stroke="{accent}" stroke-width="2"/>'
                         f'<path d="M {gx - 3} {gy - 2} L {gx - 3} {gy + 3} '
                         f'M {gx + 5} {gy + 7} L {gx + 9} {gy + 7} L {gx + 9} {gy - 6} '
                         f'L {gx + 5} {gy - 6}" fill="none" stroke="{accent}" '
                         f'stroke-width="2"/>')
        else:
            parts.append(f'<circle cx="{gx}" cy="{gy}" r="8" fill="none" '
                         f'stroke="{accent}" stroke-width="2"/>'
                         f'<path d="M {gx} {gy - 4} L {gx} {gy + 1} L {gx + 4} {gy + 1}" '
                         f'fill="none" stroke="{accent}" stroke-width="2"/>')
        parts.append(text(tx + 60, ry + 16, value, size=17, fill=H, weight="800"))
        parts.append(text(tx + 60, ry + 32, label, size=10, fill=MU))
    ex = tx + tw + 16
    ew = CW - lw - tw - 32
    parts.append(card(ex, y, ew, 200, rx=14))
    parts.append(text(ex + 16, y + 30, "LeetCode Progress", size=13.5, fill=H,
                      weight="800"))
    parts.append(text(ex + ew - 16, y + 30, "Profile →", size=11, fill=LC,
                      weight="700", anchor="end"))
    parts.append(text(ex + 16, y + 64, str(lc["solved"]), size=26, fill=LC,
                      weight="800"))
    parts.append(text(ex + 16 + len(str(lc["solved"])) * 16 + 8, y + 64,
                      "Solved Problems", size=11, fill=MU))
    diff = [(d["difficulty"], d["count"]) for d in lc["by_diff"] if d["difficulty"] != "All"]
    mx = max(c for _, c in diff) or 1
    dcol = {"Easy": "#00b8a3", "Medium": "#ffc01e", "Hard": "#ff375f"}
    for i, (name, cnt) in enumerate(diff):
        by = y + 84 + i * 30
        parts.append(text(ex + 16, by + 4, name, size=10.5, fill=T, weight="600"))
        parts.append(text(ex + ew - 16, by + 4, str(cnt), size=10.5, fill=H,
                          weight="700", anchor="end"))
        parts.append(rect(ex + 16, by + 10, ew - 32, 6, "#1c2433", rx=3))
        parts.append(rect(ex + 16, by + 10, (ew - 32) * cnt / mx, 6, dcol[name], rx=3))
    parts.append(text(ex + 16, y + 186, f"Global Ranking #{lc['ranking']:,}", size=10.5,
                      fill=MU))
    return hgt, "\n".join(parts)


def build_achievements(badges, lc_badges, lc):
    hgt = 226
    parts = [heading(26, "Achievements", emoji="🏆",
                     sub="Badges and milestones from GitHub and LeetCode.")]
    y = 62
    parts.append(card(M, y, CW, 148, rx=14))
    gh_badges = [(b["img"], b["label"]) for b in badges]
    positions = [M + 110, M + 270, M + 430]
    for (img, label), hx in zip(gh_badges, positions):
        parts.append(f'<path d="{hexpath(hx, y + 58, 44)}" fill="#161e2b" '
                     f'stroke="url(#ring)" stroke-width="2.5"/>')
        parts.append(f'<image href="data:image/png;base64,{img}" x="{hx - 30}" '
                     f'y="{y + 28}" width="60" height="60"/>')
        parts.append(text(hx, y + 124, label, size=11.5, fill=H, weight="700",
                          anchor="middle"))
    hx = M + 590
    parts.append(f'<path d="{hexpath(hx, y + 58, 44)}" fill="#241d10" '
                 f'stroke="{LC}" stroke-width="2.5"/>')
    parts.append(text(hx, y + 56, str(lc["solved"]), size=26, fill=LC, weight="800",
                      anchor="middle"))
    parts.append(text(hx, y + 76, "Solved", size=11, fill="#ffe0a8", anchor="middle"))
    parts.append(text(hx, y + 124, "LeetCode", size=11.5, fill=H, weight="700",
                      anchor="middle"))
    px, py = M + 700, y + 34
    for label in lc_badges:
        pw = len(label) * 6.4 + 26
        if px + pw > M + CW - 16:
            px, py = M + 700, py + 34
        parts.append(pill(px, py, pw, 26, label, size=10.5, fill="#241d10",
                          stroke="#6b4a12", tcolor="#ffd88a", weight="600"))
        px += pw + 8
    parts.append(text(M + 700, y + 112, "Always shipping, always learning.", size=12,
                      fill=MU, style="italic"))
    parts.append(text(M + 700, y + 134, "Star ⭐ the repos if they help you!", size=12.5,
                      fill=ACC, weight="600"))
    return hgt, "\n".join(parts)


def build_journey():
    hgt = 322
    parts = [heading(26, "My Journey", emoji="🧭",
                     sub="A timeline of my learning, projects, and achievements.")]
    y = 62
    lw = CW
    parts.append(card(M, y, lw, 130, rx=14))
    entries = [
        ("2023", "Started learning", "web development", ACC),
        ("2024", "Built interactive", "JS projects", ACC),
        ("2025", "Full-stack MERN", "applications", ACC),
        ("2026", "Teen Helpline &", "profile dashboards", ACC),
        ("Now", "Open to full-time", "roles & collabs", GREEN),
    ]
    line_y = y + 44
    x0 = M + 95
    step = (CW - 190) / 4
    parts.append(f'<line x1="{x0}" y1="{line_y}" x2="{x0 + step * 4}" y2="{line_y}" '
                 f'stroke="{BORDER}" stroke-width="2"/>')
    parts.append(f'<line x1="{x0 + step * 3}" y1="{line_y}" x2="{x0 + step * 4}" '
                 f'y2="{line_y}" stroke="{GREEN}" stroke-width="2"/>')
    for i, (year, l1, l2, color) in enumerate(entries):
        cx = x0 + step * i
        parts.append(f'<circle cx="{cx}" cy="{line_y}" r="7" fill="{PAGE}" '
                     f'stroke="{color}" stroke-width="3"/>')
        parts.append(text(cx, y + 32, year, size=13, fill=color, weight="800",
                          anchor="middle"))
        parts.append(text(cx, y + 72, l1, size=11, fill=T, anchor="middle"))
        parts.append(text(cx, y + 88, l2, size=11, fill=T, anchor="middle"))
    qy = y + 144
    parts.append(card(M, qy, CW, 100, rx=14, fill="#141024"))
    parts.append(f'<clipPath id="qclip"><rect x="{M + 1}" y="{qy + 1}" width="{CW - 2}" '
                 f'height="98" rx="13"/></clipPath>')
    parts.append(f'<g clip-path="url(#qclip)">'
                 + rect(M, qy, CW, 100, "url(#qsky)")
                 + city_scape(qy + 20, qy + 100, 33, "#191340", hmin=30, hmax=76)
                 + rect(M, qy + 84, CW, 16, "#0c0918")
                 + rect(M, qy, CW, 100, "url(#fade)")
                 + '</g>')
    parts.append(f'<path d="{M + 1} {qy + 1} L {M + CW - 1} {qy + 1} '
                 f'L {M + CW - 1} {qy + 99} L {M + 1} {qy + 99} Z" fill="none" '
                 f'stroke="{BORDER}" stroke-width="1.2"/>')
    parts.append(text(M + 300, qy + 44, "“", size=44, fill=ACC, weight="800",
                      family="Georgia, serif"))
    parts.append(text(M + 334, qy + 46,
                      "Consistency builds skills, projects build experience,", size=14.5,
                      fill=H, style="italic"))
    parts.append(text(M + 334, qy + 70,
                      "and both build a better you.”", size=14.5, fill=H,
                      style="italic"))
    parts.append(text(M + CW - 40, qy + 88, "— Ashish Vibhor", size=12.5, fill="#aeb8cc",
                      anchor="end"))
    return hgt, "\n".join(parts)


def build_connect(icons):
    hgt = 174
    parts = [heading(26, "Let's Connect", emoji="✈️",
                     sub="Always open to interesting projects, collaborations and "
                         "opportunities.")]
    y = 62
    btns = [("linkedin", "LinkedIn", "#0A66C2"), ("github", "GitHub", "#161b22"),
            ("leetcode", "LeetCode", LC), ("gmail", "Email", "#D14836")]
    bw = 131
    for i, (slug, label, color) in enumerate(btns):
        x = M + i * (bw + 12)
        parts.append(rect(x, y, bw, 52, color, rx=10,
                          stroke=BORDER if slug == "github" else "none"))
        if slug in icons:
            parts.append(icon_img(icons[slug], x + 16, y + 14, 24))
            parts.append(text(x + 48, y + 33, label, size=14, fill="#ffffff",
                              weight="700"))
        elif slug == "linkedin":
            parts.append(rect(x + 16, y + 14, 24, 24, "#ffffff", rx=5))
            parts.append(text(x + 28, y + 32, "in", size=13, fill="#0A66C2",
                              weight="800", anchor="middle"))
            parts.append(text(x + 48, y + 33, label, size=14, fill="#ffffff",
                              weight="700"))
    cx = M + 4 * (bw + 12) + 8
    cwid = CW - 4 * (bw + 12) - 8
    parts.append(card(cx, y, cwid, 96, rx=14, fill=CARD2))
    rows = [("✉", "ashis2489@gmail.com", "Drop me an email"),
            ("📍", "India", "Based in India"),
            ("●", "Open to opportunities", "Let's build something great!")]
    for i, (glyph, main, sub) in enumerate(rows):
        ry = y + 20 + i * 26
        gcol = GREEN if glyph == "●" else ACC
        parts.append(text(cx + 18, ry + 6, glyph, size=12, fill=gcol))
        parts.append(text(cx + 42, ry + 5, main, size=11.5, fill=H, weight="700"))
        parts.append(text(cx + 42 + len(main) * 6.4 + 14, ry + 5, sub, size=10.5,
                          fill=MU))
    return hgt, "\n".join(parts)


def build_footer(gh_icon):
    hgt = 64
    parts = [rect(0, 0, W, hgt, "#0b111c")]
    parts.append(f'<line x1="0" y1="0" x2="{W}" y2="0" stroke="{BORDER}"/>')
    parts.append(rect(M, 17, 30, 30, "#161e2b", rx=8, stroke=BORDER))
    parts.append(f'<path d="M {M + 11} {32 - 7} L {M + 22} {32} L {M + 11} {32 + 7} Z" '
                 f'fill="{CY}"/>')
    parts.append(text(M + 40, 32, "ASHISH", size=14, fill=H, weight="800"))
    parts.append(text(M + 40, 48, "Full-Stack Developer | India", size=10, fill=MU))
    tabs = ["Home", "About", "Projects", "Skills", "Stats", "Achievements", "Contact"]
    x = W / 2 - 210
    for t in tabs:
        parts.append(text(x, 37, t, size=11.5, fill=MU))
        x += len(t) * 6.4 + 18
    parts.append(text(W - M - 46, 37, "Code. Create. Contribute. Repeat.", size=11,
                      fill=MU, anchor="end"))
    parts.append(rect(W - M - 34, 17, 30, 30, "#161e2b", rx=8, stroke=BORDER))
    parts.append(f'<path d="M {W - M - 19} {40} L {W - M - 19} {26} M {W - M - 25} {32} '
                 f'L {W - M - 19} {26} L {W - M - 13} {32}" fill="none" stroke="{ACC}" '
                 f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    return hgt, "\n".join(parts)


def main():
    OUT.mkdir(exist_ok=True)
    user = gh(f"users/{OWNER}")
    stats = {
        "repos": user["public_repos"],
        "commits": gh(f"search/commits?q=author:{OWNER}")["total_count"],
        "prs": gh(f"search/issues?q=type:pr+author:{OWNER}")["total_count"],
        "issues": gh(f"search/issues?q=type:issue+author:{OWNER}+state:closed")["total_count"],
    }
    contrib = gh("graphql", "-f",
                 "query=query($login:String!){user(login:$login){contributionsCollection"
                 "{contributionCalendar{totalContributions weeks{contributionDays"
                 "{contributionCount date}}}}}}", "-f", f"login={OWNER}")
    contrib = contrib["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    lc_q = json.dumps({"query": "query u($username:String!){matchedUser(username:$username)"
                       "{profile{ranking} submitStatsGlobal{acSubmissionNum"
                       "{difficulty count}}}}",
                       "variables": {"username": LC_USER}}).encode()
    lc_raw = json.loads(fetch("https://leetcode.com/graphql/", data=lc_q))
    mu = lc_raw["data"]["matchedUser"]
    ac = {d["difficulty"]: d["count"] for d in mu["submitStatsGlobal"]["acSubmissionNum"]}
    lc = {"solved": ac.get("All", 0), "ranking": mu["profile"]["ranking"],
          "by_diff": mu["submitStatsGlobal"]["acSubmissionNum"]}
    lc_badges = ["Annual Badge", "Daily Coding Challenge"]

    colors = {"typescript": "3178C6", "react": "61DAFB", "nextdotjs": "FFFFFF",
              "nodedotjs": "5FA04E", "tailwindcss": "06B6D4", "redux": "764ABC",
              "mongodb": "47A248", "postgresql": "4169E1", "prisma": "FFFFFF",
              "firebase": "DD2C00", "express": "FFFFFF", "docker": "2496ED",
              "git": "F05032", "vercel": "FFFFFF", "figma": "F24E1E",
              "html5": "E34F26", "javascript": "F7DF1E", "github": "FFFFFF",
              "gmail": "EA4335", "cplusplus": "00599C", "css": "1572B6",
              "postman": "FF6C37", "leetcode": "FFA116"}
    icons = {}
    for slug, color in colors.items():
        try:
            icons[slug] = base64.b64encode(
                fetch(f"https://cdn.simpleicons.org/{slug}/{color}")).decode()
        except Exception:
            print("icon missing:", slug)

    projects = [
        {"name": "teen-helpline", "title": "Teen Helpline", "letter": "T", "accent": "#3178C6",
         "desc": "Mental wellness platform — counselling booking, journal, mood tracking "
                 "& community.",
         "tags": ["Next.js", "Prisma", "TypeScript", "Tailwind"]},
        {"name": "work-", "title": "Employee Management", "letter": "W", "accent": "#F7DF1E",
         "desc": "MERN employee records app — full CRUD dashboard for teams.",
         "tags": ["React", "Node.js", "MongoDB", "Express"]},
        {"name": "github-badges", "title": "GitHub Badges", "letter": "B", "accent": "#8B5CF6",
         "desc": "Profile badges and README widget collection for developers.",
         "tags": ["Markdown", "Badges", "Actions"]},
        {"name": "priv", "title": "Portfolio Website", "letter": "P", "accent": "#06B6D4",
         "desc": "3D developer portfolio and profile README experiments.",
         "tags": ["TypeScript", "3D Web", "SVG"]},
    ]
    for p in projects:
        p["thumb"] = base64.b64encode(
            fetch(f"https://opengraph.githubassets.com/1/{OWNER}/{p['name']}")).decode()

    badges = []
    for slug, label in [("pull-shark", "Pull Shark"), ("quickdraw", "Quickdraw"),
                        ("yolo", "Yolo")]:
        badges.append({"label": label, "img": base64.b64encode(fetch(
            f"https://github.githubassets.com/images/modules/profile/achievements/"
            f"{slug}-default.png")).decode()})

    avatar_b64 = base64.b64encode(pathlib.Path("assets/avatar.png").read_bytes()).decode()

    def li_box(x, y):
        return (rect(x, y, 16, 16, "#ffffff", rx=3)
                + text(x + 8, y + 12, "in", size=10, fill="#0A66C2", weight="800",
                       anchor="middle"))

    sections = [
        ("nav", build_nav(icons["github"], li_box)),
        ("hero", build_hero(icons)),
        ("strip", build_strip()),
        ("about", build_about(avatar_b64)),
        ("tech", build_tech(icons)),
        ("projects", build_projects(projects, icons["github"],
                                    [(b["img"], b["label"]) for b in badges])),
        ("stats", build_stats(contrib, stats, lc, icons)),
        ("achievements", build_achievements(badges, lc_badges, lc)),
        ("journey", build_journey()),
        ("connect", build_connect(icons)),
        ("footer", build_footer(icons["github"])),
    ]
    off, yy = {}, 0
    for n, (h, _) in sections:
        off[n] = yy
        yy += h
    total = yy
    parts = [rect(0, 0, W, total, PAGE)]
    for n, (h, body) in sections:
        parts.append(f'<g transform="translate(0 {off[n]})">{body}</g>')
    css = "@keyframes pulse { 0%,100% { opacity: .55; r: 5 } 50% { opacity: 1; r: 6.5 } }"
    PAGE_SVG.write_text(svg_doc(W, total, "\n".join(parts), css), encoding="utf-8")

    links = {
        "profile": f"https://github.com/{OWNER}",
        "search": f"https://github.com/search?q=user%3A{OWNER}&type=repositories",
        "gh": f"https://github.com/{OWNER}",
        "li": f"https://linkedin.com/in/{LINKEDIN}/",
        "repos": f"https://github.com/{OWNER}?tab=repositories",
        "leetcode": f"https://leetcode.com/u/{LC_USER}/",
        "teen": f"https://github.com/{OWNER}/teen-helpline",
        "work": f"https://github.com/{OWNER}/work-",
        "badges": f"https://github.com/{OWNER}/github-badges",
        "priv": f"https://github.com/{OWNER}/priv",
        "commits": f"https://github.com/search?q=author%3A{OWNER}&type=commits",
        "mailto": "mailto:ashis2489@gmail.com",
    }
    alts = {
        "profile": "Ashish on GitHub", "search": "Search Ashish's repositories",
        "gh": "GitHub", "li": "LinkedIn", "repos": "All repositories",
        "leetcode": "LeetCode profile", "teen": "Teen Helpline repo",
        "work": "Employee Management repo", "badges": "GitHub Badges repo",
        "priv": "Portfolio repo", "commits": "Ashish's commits",
        "mailto": "Email Ashish",
    }
    rows = [
        ("nav", "nav", 0, 54, [(0, 716, "profile"), (716, 876, "search"),
                               (876, 919, "gh"), (919, 1000, "li")]),
        ("hero", "hero", 0, 330, [(0, 1000, "profile")]),
        ("strip", "strip", 0, 76, [(0, 261, "profile"), (261, 500, "repos"),
                                   (500, 739, "repos"), (739, 1000, "leetcode")]),
        ("about", "about", 0, 250, [(0, 1000, None)]),
        ("tech", "tech", 0, 162, [(0, 1000, None)]),
        ("phead", "projects", 0, 62, [(0, 828, None), (828, 1000, "repos")]),
        ("prow1", "projects", 62, 306, [(0, 338.3, "teen"), (338.3, 661.7, "work"),
                                        (661.7, 1000, "badges")]),
        ("prow2", "projects", 306, 582, [(0, 338.3, "priv"), (338.3, 661.7, "repos"),
                                         (661.7, 1000, "badges")]),
        ("shead", "stats", 0, 62, [(0, 1000, None)]),
        ("srow", "stats", 62, 278, [(0, 530, "profile"), (530, 722, "commits"),
                                    (722, 1000, "leetcode")]),
        ("ahead", "achievements", 0, 62, [(0, 1000, None)]),
        ("arow", "achievements", 62, 226, [(0, 532, "profile"), (532, 1000, "leetcode")]),
        ("journey", "journey", 0, 322, [(0, 1000, None)]),
        ("chead", "connect", 0, 62, [(0, 1000, None)]),
        ("crow", "connect", 62, 174, [(0, 159, "li"), (159, 302, "gh"),
                                      (302, 445, "leetcode"), (445, 1000, "mailto")]),
        ("footer", "footer", 0, 64, [(0, 1000, "profile")]),
    ]
    tiles_dir = OUT / "tiles"
    tiles_dir.mkdir(exist_ok=True)
    img_re = re.compile(r'<image [^>]* x="(-?[\d.]+)" y="(-?[\d.]+)"[^>]*/>')
    body_by_sec = {n: b for n, (h, b) in sections}
    html_lines = ['<div align="center">']
    n_tiles = 0
    for rname, sec, ly0, ly1, slices in rows:
        hgt = ly1 - ly0
        y0 = off[sec] + ly0
        body = body_by_sec[sec]
        defs = "" if 'id="sky"' in body else scene_defs()
        seg = []
        for i, (x0, x1, key) in enumerate(slices):
            pct = (x1 - x0) / 10
            if len(slices) > 1 and i == len(slices) - 1:
                pct -= 0.05
            filt = lambda m: (m.group(0)
                              if x0 - 8 <= float(m.group(1)) <= x1 + 8
                              and ly0 - 8 <= float(m.group(2)) <= ly1 + 8 else "")
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                   f'viewBox="{x0} {y0} {x1 - x0} {hgt}" '
                   f'width="{x1 - x0}" height="{hgt}">\n'
                   f'<style>{css}</style>\n{defs}\n'
                   f'<g transform="translate(0 {off[sec]})">'
                   f'{img_re.sub(filt, body)}</g>\n</svg>\n')
            fn = f"{rname}{i}.svg"
            (tiles_dir / fn).write_text(svg, encoding="utf-8")
            n_tiles += 1
            alt = alts.get(key) or f"{rname} section"
            img = (f'<img align="top" width="{pct:.2f}%" '
                   f'src="./assets/tiles/{fn}" alt="{esc(alt)}">')
            seg.append(f'<a href="{links[key]}">{img}</a>' if key else img)
        html_lines.append("".join(seg))
    html_lines.append("</div>")

    readme = f'''{chr(10).join(html_lines)}

<div align="center">
  <a href="https://github.com/{OWNER}"><img src="https://img.shields.io/badge/Follow-%40{OWNER}-0969da?style=for-the-badge&logo=github&logoColor=white&labelColor=0d1117" alt="Follow @{OWNER}" /></a>
  <a href="https://linkedin.com/in/{LINKEDIN}"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=0d1117" alt="LinkedIn" /></a>
  <a href="https://leetcode.com/u/{LC_USER}/"><img src="https://img.shields.io/badge/LeetCode-{lc["solved"]}%20Solved-FFA116?style=for-the-badge&logo=leetcode&logoColor=white&labelColor=0d1117" alt="LeetCode — {lc["solved"]} solved" /></a>
  <a href="mailto:ashis2489@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white&labelColor=0d1117" alt="Email" /></a>
  <img src="https://komarev.com/ghpvc/?username={OWNER}&style=for-the-badge&color=00f2fe&labelColor=0d1117&label=PROFILE+VIEWS" alt="Profile views" />
</div>

<details>
  <summary><b>🖥️ Run <code>ashis.exe</code> — click to boot specs</b></summary>
  <br/>

```typescript
const ashis: Developer = {{
  name:        "Ashish Vibhor",
  username:    "{OWNER}",
  leetcode:    "{LC_USER}",
  role:        "Full-Stack Web Developer",
  location:    "India 🇮🇳",
  stack:       ["React", "Next.js", "TypeScript", "Node.js"],
  learning:    ["System Design", "AWS", "Cloud Architecture"],
  openTo:      ["Collaborations", "Freelance", "Full-time"],
  funFact:     "I debug with console.log and I'm not ashamed 🙈",
  motto:       "Code. Create. Contribute. Repeat. ⚡"
}};
```

</details>

### Recent activity

<!--START_SECTION:activity-->
<!--END_SECTION:activity-->

<details>
  <summary>⌨️ Coding stats</summary>
  <br/>

  <!--START_SECTION:waka-->
  <!--END_SECTION:waka-->

</details>

<details>
  <summary>🐍 Contribution snake</summary>
  <br/>

  <img src="https://raw.githubusercontent.com/{OWNER}/{OWNER}/output/github-contribution-grid-snake-dark.svg" width="100%" alt="Contribution snake animation" />

</details>
'''
    pathlib.Path("README.md").write_text(readme, encoding="utf-8")
    pathlib.Path("preview.html").write_text(
        "<html><body style='background:#010409;margin:0;width:1000px'>"
        + "\n".join(html_lines) + "</body></html>",
        encoding="utf-8")
    tiles_bytes = sum(p.stat().st_size for p in tiles_dir.glob("*.svg"))
    print(f"page.svg: {total}px tall, {PAGE_SVG.stat().st_size} bytes | "
          f"{n_tiles} tiles, {tiles_bytes} bytes | "
          f"stats={stats} | lc solved={lc['solved']} rank={lc['ranking']}")


if __name__ == "__main__":
    main()
