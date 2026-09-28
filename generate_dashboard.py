"""Generate the full-page dark dashboard SVG for the profile README. Run: python generate_dashboard.py"""
import base64
import datetime
import html
import json
import pathlib
import random
import subprocess
import urllib.request

OWNER = "ashis2489"
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


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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


def heading(y, label, emoji=None, chip=None):
    parts = []
    x = M
    if emoji:
        parts.append(text(x, y, emoji, size=17))
        x += 30
    parts.append(text(x, y, label, size=20, fill=H, weight="800"))
    lx = x + len(label) * 11 + 12
    parts.append(rect(lx, y - 8, 26, 3, ACC, rx=1.5))
    if chip:
        cw = len(chip) * 6.6 + 26
        parts.append(pill(W - M - cw, y - 17, cw, 26, chip, size=11, fill=CARD2,
                          tcolor=ACC, weight="600"))
    return "\n".join(parts)


def build_nav(gh_icon):
    hgt = 54
    parts = [rect(0, 0, W, hgt, "#0b111c")]
    parts.append(icon_img(gh_icon, M, 14, 26))
    tabs = ["Overview", "Projects", "Stats", "Achievements", "Contact"]
    x = M + 46
    for i, t in enumerate(tabs):
        active = i == 0
        parts.append(text(x, 33, t, size=13, fill=H if active else MU,
                          weight="700" if active else "500"))
        tw = len(t) * 7.2
        if active:
            parts.append(rect(x, 50, tw, 3, CY, rx=1.5))
        x += tw + 26
    sx = W - M - 250
    parts.append(rect(sx, 12, 250, 30, "#0d141f", rx=8, stroke=BORDER))
    parts.append(text(sx + 14, 31, "Search my work...", size=12, fill=MU))
    parts.append(rect(sx + 224, 17, 20, 20, "#161e2b", rx=5, stroke=BORDER))
    parts.append(text(sx + 234, 31, "/", size=11, fill=MU, anchor="middle"))
    parts.append(f'<line x1="0" y1="{hgt}" x2="{W}" y2="{hgt}" stroke="{BORDER}"/>')
    return hgt, "\n".join(parts)


def build_hero(icons):
    hgt = 404
    y0 = 54
    horizon = y0 + 340
    rnd = random.Random(11)
    stars = "".join(
        f'<circle cx="{rnd.uniform(360, W):.1f}" cy="{rnd.uniform(y0 + 6, y0 + 300):.1f}" '
        f'r="{rnd.uniform(0.4, 1.5):.1f}" fill="#dbe4ff" '
        f'opacity="{rnd.uniform(0.15, 0.75):.2f}"/>' for _ in range(80))
    parts = [rect(0, y0, W, hgt, PAGE)]
    parts.append('<defs><linearGradient id="sky2" x1="0" y1="0" x2="1" y2="1">'
                 '<stop offset="0" stop-color="#0c1524"/>'
                 '<stop offset="1" stop-color="#0a0e15"/></linearGradient>'
                 '<linearGradient id="heroG" x1="0" y1="0" x2="1" y2="0">'
                 '<stop offset="0" stop-color="#a78bfa"/>'
                 '<stop offset="0.55" stop-color="#7c9cff"/>'
                 '<stop offset="1" stop-color="#22d3ee"/></linearGradient>'
                 '<radialGradient id="moonglow">'
                 '<stop offset="0" stop-color="#f5f5dc" stop-opacity="0.5"/>'
                 '<stop offset="1" stop-color="#f5f5dc" stop-opacity="0"/></radialGradient>'
                 '</defs>')
    parts.append(rect(340, y0, 660, 340, "url(#sky2)", rx=16))
    parts.append(stars)
    parts.append(f'<circle cx="900" cy="{y0 + 56}" r="46" fill="url(#moonglow)"/>'
                 f'<circle cx="900" cy="{y0 + 56}" r="23" fill="#f2f0da"/>')
    parts.append(f'<path d="M340 {horizon} L470 {horizon - 96} L560 {horizon - 34} '
                 f'L660 {horizon - 118} L790 {horizon - 30} L900 {horizon - 84} '
                 f'L1000 {horizon - 16} L1000 {horizon} Z" fill="#132036"/>')
    parts.append(f'<path d="M340 {horizon} L445 {horizon - 54} L540 {horizon - 12} '
                 f'L640 {horizon - 66} L760 {horizon - 20} L880 {horizon - 58} '
                 f'L1000 {horizon - 8} L1000 {horizon} Z" fill="#0b1320"/>')
    for lx, ly in [(505, horizon - 40), (612, horizon - 52), (742, horizon - 30),
                   (866, horizon - 44)]:
        parts.append(f'<circle cx="{lx}" cy="{ly}" r="2" fill="#ffd47e" opacity="0.9"/>')
    parts.append(rect(M, y0 + 16, 660, 360, CARD, rx=16, stroke=BORDER))
    parts.append(text(M + 26, y0 + 52, "Hey, I'm", size=15, fill=MU, family=MONO))
    parts.append(text(M + 24, y0 + 116, "ASHIS", size=62, fill="url(#heroG)", weight="800"))
    parts.append(f'<text x="{M + 26}" y="{y0 + 152}" font-family="{FONT}" font-size="18" '
                 f'font-weight="700" fill="{H}">Full-Stack Developer '
                 f'<tspan fill="{CY}">| Software Engineer</tspan></text>')
    parts.append(text(M + 26, y0 + 182, "I build scalable web applications and turn ideas",
                      size=13, fill=MU))
    parts.append(text(M + 26, y0 + 202, "into real-world products — UI, API and deploy.",
                      size=13, fill=MU))
    px = M + 26
    for label, w in [("Open to Opportunities", 176), ("Based in India", 128),
                     ("React · Next.js · Node.js", 186), ("TypeScript", 96)]:
        parts.append(pill(px, y0 + 222, w, 28, label, dot=label.startswith("Open"),
                          size=11.5))
        px += w + 10
    sx = M + 26
    for slug, label in [("github", "GitHub"), ("linkedin", "LinkedIn"), ("gmail", "Email")]:
        parts.append(rect(sx, y0 + 266, 44, 44, CARD2, rx=12, stroke=BORDER))
        if slug in icons:
            parts.append(icon_img(icons[slug], sx + 11, y0 + 277, 22))
        else:
            parts.append(text(sx + 22, y0 + 296, "in", size=17, fill=H, weight="800",
                              anchor="middle"))
        parts.append(text(sx + 22, y0 + 330, label, size=10.5, fill=MU, anchor="middle"))
        sx += 66
    for i, line in enumerate(["Code.", "Create.", "Contribute.", "Repeat."]):
        ry = y0 + 170 + i * 30
        parts.append(text(700, ry, line, size=22, fill="#9fb0c9", family=SCRIPT,
                          transform=f"rotate(-8 700 {ry})"))
    return hgt, "\n".join(parts)


def build_tiles():
    hgt = 104
    tiles = [
        ("calendar", "389", "Contributions (Year)"),
        ("repo", "27", "Public Repositories"),
        ("box", "4", "Featured Projects"),
        ("git-pull", "4", "Pull Requests"),
        ("spark", "Open", "To Work — Available"),
    ]
    tw = (CW - 4 * 14) / 5
    parts = []
    for i, (kind, value, label) in enumerate(tiles):
        x = M + i * (tw + 14)
        parts.append(card(x, 0, tw, hgt, rx=12))
        accent = GREEN if kind == "spark" else [ACC, "#a78bfa", CY, "#f778ba", GREEN][i]
        parts.append(rect(x + 14, 22, 44, 44, "#161e2b", rx=10, stroke=BORDER))
        gx, gy = x + 36, 44
        if kind == "calendar":
            parts.append(rect(gx - 9, gy - 8, 18, 16, "none", rx=3, stroke=accent, sw=2))
            parts.append(rect(gx - 9, gy - 12, 18, 6, "none", rx=2, stroke=accent, sw=2))
        elif kind == "repo":
            parts.append(rect(gx - 9, gy - 8, 18, 16, "none", rx=3, stroke=accent, sw=2))
            parts.append(f'<circle cx="{gx - 3}" cy="{gy}" r="2.5" fill="{accent}"/>')
        elif kind == "box":
            parts.append(f'<path d="M {gx} {gy - 10} L {gx + 10} {gy - 4} L {gx + 10} {gy + 6} '
                         f'L {gx} {gy + 12} L {gx - 10} {gy + 6} L {gx - 10} {gy - 4} Z" '
                         f'fill="none" stroke="{accent}" stroke-width="2"/>')
        elif kind == "git-pull":
            parts.append(f'<circle cx="{gx - 4}" cy="{gy - 7}" r="3.5" fill="none" '
                         f'stroke="{accent}" stroke-width="2"/>'
                         f'<circle cx="{gx - 4}" cy="{gy + 9}" r="3.5" fill="none" '
                         f'stroke="{accent}" stroke-width="2"/>'
                         f'<path d="M {gx - 4} {gy - 3} L {gx - 4} {gy + 5} M {gx + 4} {gy + 9} '
                         f'L {gx + 9} {gy + 9} L {gx + 9} {gy - 7} L {gx + 4} {gy - 7}" '
                         f'fill="none" stroke="{accent}" stroke-width="2"/>')
        else:
            parts.append(f'<path d="M {gx} {gy - 11} L {gx + 3} {gy - 2} L {gx + 12} {gy} '
                         f'L {gx + 3} {gy + 3} L {gx} {gy + 12} L {gx - 3} {gy + 3} '
                         f'L {gx - 12} {gy} L {gx - 3} {gy - 2} Z" fill="{accent}"/>')
        parts.append(text(x + 72, 48, value, size=21, fill=H, weight="800"))
        parts.append(text(x + 72, 68, label, size=10, fill=MU))
    return hgt, "\n".join(parts)


def build_about():
    hgt = 320
    parts = [heading(26, "About Me", emoji="👤")]
    left_w = 596
    y = 48
    para = ("I'm a full-stack web developer from India, passionate about building impactful "
            "products, solving real-world problems and continuously learning. I love working "
            "on full-stack development, exploring new technologies and turning ideas into "
            "scalable web applications.")
    for line in wrap(para, 92):
        parts.append(text(M, y, line, size=13.5, fill=T))
        y += 21
    y += 14
    minis = [("Design", "Craft", "Clean, responsive UI that feels right."),
             ("Build", "</>", "From idea to deployment, end to end."),
             ("Learn", "Always", "New tech, better patterns, every week.")]
    mw = (left_w - 2 * 12) / 3
    for i, (title, tag, desc) in enumerate(minis):
        x = M + i * (mw + 12)
        parts.append(card(x, y, mw, 104, rx=12, fill=CARD2))
        parts.append(rect(x + 14, y + 14, 30, 30, "#161e2b", rx=8, stroke=BORDER))
        parts.append(text(x + 29, y + 34, ["✦", "</>", "◈"][i], size=13, fill=CY,
                          anchor="middle", family=MONO))
        parts.append(text(x + 54, y + 27, title, size=13, fill=H, weight="800"))
        parts.append(text(x + 54, y + 43, tag, size=10.5, fill=ACC, weight="600"))
        for j, line in enumerate(wrap(desc, 26)[:2]):
            parts.append(text(x + 14, y + 66 + j * 15, line, size=10.5, fill=MU))
    rx0 = M + left_w + 16
    rw = CW - left_w - 16
    parts.append(card(rx0, 48, rw, hgt - 48, rx=14))
    rows = [
        ("📍", "Location", ["India"]),
        ("🎯", "Interests", ["Web Development, UI/UX, Open Source,", "System Design"]),
        ("⚡", "Currently", ["Building real-world projects &",
                             "exploring new opportunities"]),
        ("🤝", "Open to", ["Full-time roles, Freelance, Collaborations"]),
    ]
    ry = 82
    for glyph, label, vlines in rows:
        parts.append(rect(rx0 + 18, ry - 16, 34, 34, "#161e2b", rx=9, stroke=BORDER))
        parts.append(text(rx0 + 35, ry + 6, glyph, size=14, anchor="middle"))
        parts.append(text(rx0 + 64, ry - 2, label, size=13, fill=H, weight="800"))
        for j, line in enumerate(vlines):
            parts.append(text(rx0 + 64, ry + 16 + j * 15, line, size=11, fill=MU))
        ry += 34 + 15 * (len(vlines) - 1) + 16
    return hgt, "\n".join(parts)


def build_tech(icons):
    hgt = 224
    parts = [heading(26, "Tech Stack", emoji="</>",
                     chip="Always learning more →")]
    cats = [
        ("Languages", ["javascript", "typescript", "html5", "css", "cplusplus"],
         ["JS", "TS", "HTML", "CSS", "C++"]),
        ("Frontend", ["react", "nextdotjs", "tailwindcss", "redux", "figma"],
         ["React", "Next", "Tailwind", "Redux", "Figma"]),
        ("Backend", ["nodedotjs", "express", "prisma", "postman"],
         ["Node", "Express", "Prisma", "Postman"]),
        ("Database", ["mongodb", "postgresql", "firebase"],
         ["MongoDB", "Postgres", "Firebase"]),
        ("Tools & Cloud", ["git", "docker", "vercel", "github"],
         ["Git", "Docker", "Vercel", "GitHub"]),
    ]
    cw = (CW - 4 * 12) / 5
    for i, (title, slugs, labels) in enumerate(cats):
        x = M + i * (cw + 12)
        parts.append(card(x, 48, cw, hgt - 48, rx=12, fill=CARD2))
        parts.append(rect(x + 14, 62, 20, 20, "#161e2b", rx=6, stroke=BORDER))
        color = [ACC, CY, "#a78bfa", GREEN, "#f778ba"][i]
        parts.append(f'<circle cx="{x + 24}" cy="72" r="4" fill="{color}"/>')
        parts.append(text(x + 42, 77, title, size=12, fill=H, weight="800"))
        cols = 3
        iw = (cw - 20) / cols
        for j, slug in enumerate(slugs):
            col, row = j % cols, j // cols
            ix = x + 10 + col * iw + iw / 2
            iy = 96 + row * 56
            if slug in icons:
                parts.append(icon_img(icons[slug], ix - 12, iy, 24))
            parts.append(text(f"{ix:.1f}", iy + 38, labels[j], size=9.5, fill=MU,
                              anchor="middle"))
    return hgt, "\n".join(parts)


def build_projects(projects):
    hgt = 470
    parts = [heading(26, "Featured Projects", emoji="📦",
                     chip="View all repositories →")]
    cw = (CW - 16) / 2
    ch = 196
    for i, p in enumerate(projects):
        col, row = i % 2, i // 2
        x = M + col * (cw + 16)
        y = 48 + row * (ch + 16)
        parts.append(card(x, y, cw, ch, rx=14))
        if i == 0:
            parts.append(pill(x + 16, y + 14, 74, 22, "Featured", size=10,
                              fill="#1d2b4d", stroke="#2f4f8f", tcolor="#79b8ff",
                              weight="700"))
            ty = y + 64
        else:
            ty = y + 52
        parts.append(rect(x + 16, ty - 24, 34, 34, p["accent"], rx=9))
        parts.append(text(x + 33, ty - 1, p["letter"], size=17, fill="#ffffff",
                          weight="800", anchor="middle"))
        parts.append(text(x + 60, ty - 6, p["title"], size=15, fill=H, weight="800"))
        parts.append(text(x + 60, ty + 10, f"github.com/{OWNER}/{p['name']}", size=10,
                          fill=MU))
        parts.append(png_img(p["thumb"], x + cw - 176, y + 16, 160, 84, rx=8,
                             cid=f"th{i}"))
        dy = ty + 38
        for line in wrap(p["desc"], 46)[:2]:
            parts.append(text(x + 16, dy, line, size=11, fill=MU))
            dy += 15
        tx = x + 16
        for tag in p["tags"]:
            tw = len(tag) * 5.8 + 18
            parts.append(rect(tx, y + ch - 52, tw, 20, "#161e2b", rx=10, stroke=BORDER))
            parts.append(text(tx + tw / 2, y + ch - 38, tag, size=9.5, fill=T,
                              anchor="middle"))
            tx += tw + 6
        parts.append(text(x + cw - 16, y + ch - 20, "Repo →", size=11.5, fill=ACC,
                          weight="700", anchor="end"))
    return hgt, "\n".join(parts)


def heatmap_parts(x0, y0, contrib, cols=52, cell=8.5, gap=2.5, label=True):
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
        if label and (c == 0 or wd.day <= 7) and c - last_label >= 4:
            last_label = c
            parts.append(text(x0 + c * (cell + gap), y0 - 9, wd.strftime("%b"), size=9,
                              fill=MU, anchor="middle"))
    if label:
        for i, lab in [(0, "Mon"), (2, "Wed"), (4, "Fri")]:
            parts.append(text(x0 - 8, y0 + i * (cell + gap) + 8, lab, size=9, fill=MU,
                              anchor="end"))
    return parts


def build_stats(contrib, stats):
    hgt = 274
    parts = [heading(26, "GitHub Stats", emoji="📊")]
    y = 48
    lw = 640
    parts.append(card(M, y, lw, hgt - 48, rx=14))
    parts.extend(heatmap_parts(M + 54, y + 70, contrib))
    lx = M + lw + 16
    rw = CW - lw - 16
    parts.append(card(lx, y, rw, hgt - 48, rx=14))
    rows = [("662", "Total Commits"), (str(stats["prs"]), "Pull Requests"),
            (str(stats["issues"]), "Issues Resolved")]
    ry = y + 56
    for value, label in rows:
        parts.append(rect(lx + 20, ry - 22, 40, 40, "#161e2b", rx=10, stroke=BORDER))
        parts.append(f'<circle cx="{lx + 40}" cy="{ry - 2}" r="5" fill="{ACC}"/>')
        parts.append(text(lx + 74, ry - 4, value, size=19, fill=H, weight="800"))
        parts.append(text(lx + 74, ry + 14, label, size=10.5, fill=MU))
        ry += 62
    return hgt, "\n".join(parts)


def build_achievements(badges):
    hgt = 196
    parts = [heading(26, "Achievements", emoji="🏆")]
    parts.append(card(M, 48, CW, hgt - 48, rx=14))
    parts.append(text(M + 24, 84, "GitHub Achievements", size=13.5, fill=H, weight="800"))
    x = M + 30
    for b in badges:
        parts.append(f'<image href="data:image/png;base64,{b["img"]}" x="{x}" y="98" '
                     f'width="72" height="72"/>')
        parts.append(text(x + 36, 186, b["label"], size=10.5, fill=MU, anchor="middle"))
        x += 170
    parts.append(text(M + 560, 120, "Always shipping, always learning.", size=12,
                      fill=MU, style="italic"))
    parts.append(text(M + 560, 146, "Star ⭐ the repos if they help you!", size=12.5,
                      fill=ACC, weight="600"))
    return hgt, "\n".join(parts)


def build_journey():
    hgt = 306
    parts = [heading(26, "My Journey", emoji="🧭")]
    lw = 596
    parts.append(card(M, 48, lw, hgt - 48, rx=14))
    entries = [
        ("2023", "First web projects — HTML, CSS & JavaScript builds"),
        ("2024", "Internship assignments & interactive JS projects"),
        ("2025", "Full-stack builds — task managers, e-learning, e-commerce"),
        ("2026", "Teen Helpline platform & profile dashboards"),
        ("Now", "Open to full-time roles and collaborations"),
    ]
    ty = 84
    line_x = M + 44
    parts.append(f'<line x1="{line_x}" y1="{ty}" x2="{line_x}" y2="{ty + 4 * 50}" '
                 f'stroke="{BORDER}" stroke-width="2"/>')
    for i, (year, msg) in enumerate(entries):
        cy = ty + i * 50
        color = GREEN if i == len(entries) - 1 else ACC
        parts.append(f'<circle cx="{line_x}" cy="{cy}" r="7" fill="{PAGE}" '
                     f'stroke="{color}" stroke-width="3"/>')
        parts.append(text(M + 70, cy + 4, year, size=12.5, fill=color, weight="800"))
        parts.append(text(M + 140, cy + 4, msg, size=12, fill=T))
    qx = M + lw + 16
    qw = CW - lw - 16
    parts.append(card(qx, 48, qw, hgt - 48, rx=14, fill=CARD2))
    parts.append(text(qx + 26, 110, "“", size=54, fill=ACC, weight="800",
                      family="Georgia, serif"))
    quote = ["Consistency builds skills,", "projects build experience,",
             "and both build a better you."]
    for i, line in enumerate(quote):
        parts.append(text(qx + 30, 134 + i * 24, line, size=14, fill=T, style="italic"))
    parts.append(text(qx + qw - 30, 232, "— Ashis", size=13, fill=MU, anchor="end"))
    return hgt, "\n".join(parts)


def build_connect(icons):
    hgt = 168
    parts = [heading(26, "Let's Connect", emoji="✈️")]
    parts.append(text(M, 62, "Always open to interesting projects, collaborations and "
                             "opportunities.", size=13, fill=MU))
    btns = [("linkedin", "LinkedIn", "#0A66C2"), ("github", "GitHub", "#161b22"),
            ("gmail", "Email", "#D14836")]
    bw = (CW - 2 * 16) / 3
    for i, (slug, label, color) in enumerate(btns):
        x = M + i * (bw + 16)
        parts.append(rect(x, 84, bw, 52, color, rx=10,
                          stroke=BORDER if slug == "github" else "none"))
        if slug in icons:
            parts.append(icon_img(icons[slug], x + bw / 2 - 66, 98, 24))
            parts.append(text(x + bw / 2 + 6, 117, label, size=15, fill="#ffffff",
                              weight="700", anchor="middle"))
        else:
            parts.append(rect(x + bw / 2 - 66, 98, 24, 24, "#ffffff", rx=5))
            parts.append(text(x + bw / 2 - 54, 116, "in", size=14, fill="#0A66C2",
                              weight="800", anchor="middle"))
            parts.append(text(x + bw / 2 + 6, 117, label, size=15, fill="#ffffff",
                              weight="700", anchor="middle"))
    return hgt, "\n".join(parts)


def build_footer(gh_icon):
    hgt = 58
    parts = [rect(0, 0, W, hgt, "#0b111c")]
    parts.append(f'<line x1="0" y1="0" x2="{W}" y2="0" stroke="{BORDER}"/>')
    parts.append(icon_img(gh_icon, M, 16, 26))
    parts.append(text(M + 36, 35, "Ashis Kumar", size=13, fill=H, weight="800"))
    parts.append(text(M + 140, 35, "|  Built with ❤  |  Full-Stack Developer  |  India",
                      size=12, fill=MU))
    parts.append(text(W - M, 35, "Code. Create. Contribute. Repeat. ↗", size=12.5,
                      fill=ACC, anchor="end", weight="600"))
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

    colors = {"typescript": "3178C6", "react": "61DAFB", "nextdotjs": "FFFFFF",
              "nodedotjs": "5FA04E", "tailwindcss": "06B6D4", "redux": "764ABC",
              "mongodb": "47A248", "postgresql": "4169E1", "prisma": "FFFFFF",
              "firebase": "DD2C00", "express": "FFFFFF", "docker": "2496ED",
              "git": "F05032", "vercel": "FFFFFF", "figma": "F24E1E",
              "html5": "E34F26", "javascript": "F7DF1E", "github": "FFFFFF",
              "gmail": "EA4335", "cplusplus": "00599C", "css": "1572B6",
              "postman": "FF6C37"}
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
        {"name": "priv", "title": "VEDAA Portfolio", "letter": "P", "accent": "#06B6D4",
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

    builders = [build_nav(icons["github"]), build_hero(icons), build_tiles(),
                build_about(), build_tech(icons), build_projects(projects),
                build_stats(contrib, stats), build_achievements(badges),
                build_journey(), build_connect(icons), build_footer(icons["github"])]
    total = sum(h for h, _ in builders)
    parts = [rect(0, 0, W, total, PAGE)]
    y = 0
    for h, body in builders:
        parts.append(f'<g transform="translate(0 {y})">{body}</g>')
        y += h
    css = "@keyframes pulse { 0%,100% { opacity: .55; r: 5 } 50% { opacity: 1; r: 6.5 } }"
    PAGE_SVG.write_text(svg_doc(W, total, "\n".join(parts), css), encoding="utf-8")
    pathlib.Path("preview.html").write_text(
        "<html><body style='background:#010409;margin:0'>"
        "<img src='assets/page.svg' style='width:1000px;display:block'></body></html>",
        encoding="utf-8")
    print(f"page.svg: {total}px tall, {PAGE_SVG.stat().st_size} bytes | stats: {stats}")


if __name__ == "__main__":
    main()
