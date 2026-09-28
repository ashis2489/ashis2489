"""Generate the dark dashboard SVGs for the profile README. Run: python generate_dashboard.py"""
import base64
import html
import json
import math
import pathlib
import random
import subprocess
import urllib.request

OWNER = "ashis2489"
OUT = pathlib.Path("assets/dash")
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Cascadia Code', 'Fira Code', Consolas, monospace"

CARD_BG = "#0d1117"
CARD_BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"


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


def text(x, y, s, size=13, fill=TEXT, weight="400", anchor="start", family=None, style="normal", opacity=None):
    extra = f' opacity="{opacity}"' if opacity is not None else ""
    fam = family or FONT
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" font-style="{style}"{extra}>{esc(s)}</text>')


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1, opacity=None):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{op}/>'


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


def svg_doc(w, h, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'<style>{css}</style>\n{body}\n</svg>\n')


def card(w, h, rx=12):
    return rect(0.5, 0.5, w - 1, h - 1, CARD_BG, rx=rx, stroke=CARD_BORDER, sw=1)


def avatar_block(b64, cx, cy, r_out):
    c = 2 * math.pi * r_out
    return f'''
  <defs>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#00F2FE"/><stop offset="0.5" stop-color="#58a6ff"/>
      <stop offset="1" stop-color="#0969da"/>
    </linearGradient>
    <clipPath id="face"><circle cx="{cx}" cy="{cy}" r="{r_out - 8}"/></clipPath>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{r_out}" fill="{CARD_BG}"/>
  <image href="data:image/png;base64,{b64}" x="{cx - r_out + 8}" y="{cy - r_out + 8}"
         width="{2 * (r_out - 8)}" height="{2 * (r_out - 8)}" clip-path="url(#face)"
         preserveAspectRatio="xMidYMid slice"/>
  <circle cx="{cx}" cy="{cy}" r="{r_out}" fill="none" stroke="#21262d" stroke-width="6"/>
  <circle cx="{cx}" cy="{cy}" r="{r_out}" fill="none" stroke="url(#ring)" stroke-width="6"
          stroke-linecap="round" stroke-dasharray="140 {c - 140:.2f}"
          style="animation: sweep 3.5s linear infinite"/>'''


SWEEP_CSS = "@keyframes sweep { to { stroke-dashoffset: -%s; } }"
PULSE_CSS = '@keyframes pulse { 0%,100% { opacity: .55; r: 5 } 50% { opacity: 1; r: 6.5 } }'


def build_sidebar(avatar_b64):
    w, h = 260, 690
    y = 0
    parts = [card(w, h)]
    parts.append(avatar_block(avatar_b64, 130, 104, 74))
    y = 214
    parts.append(text(130, y, "Ashis", size=27, weight="800", fill="#ffffff", anchor="middle"))
    parts.append(text(130, y + 24, "@ashis2489", size=13, fill=MUTED, anchor="middle"))
    y += 56
    for line in wrap("Full-Stack Developer building clean, scalable web products end-to-end.", 36):
        parts.append(text(20, y, line, size=11.5, fill=MUTED))
        y += 17
    y += 8
    parts.append(f'<line x1="20" y1="{y}" x2="{w - 20}" y2="{y}" stroke="{CARD_BORDER}"/>')
    y += 26
    rows = [
        ("📍", "India"),
        ("🔗", "linkedin.com/in/ashis2489"),
        ("✉️", "ashis2489@gmail.com"),
        ("📊", "662 commits · 27 public repos"),
    ]
    for glyph, label in rows:
        parts.append(text(20, y, glyph, size=12))
        parts.append(text(42, y, label, size=11.5, fill=TEXT))
        y += 24
    y += 8
    parts.append(rect(20, y, w - 40, 34, "#161b22", rx=8, stroke=ACCENT, sw=1.4))
    parts.append(text(130, y + 22, "+  Follow @ashis2489", size=12.5, fill=ACCENT,
                      weight="700", anchor="middle"))
    y += 66
    parts.append(text(20, y, "Pinned", size=15, weight="800", fill="#ffffff"))
    y += 24
    pinned = [
        ("teen-helpline", "#3178C6"),
        ("work-", "#F7DF1E"),
        ("github-badges", "#8B5CF6"),
        ("priv", "#06B6D4"),
    ]
    for name, color in pinned:
        parts.append(rect(20, y - 12, 15, 15, color, rx=4))
        parts.append(text(44, y, name, size=12, fill=TEXT))
        y += 30
    y += 6
    parts.append(text(20, y, "Open to opportunities, always.", size=10.5, fill=MUTED, style="italic"))
    css = SWEEP_CSS % f"{2 * math.pi * 74:.2f}"
    return svg_doc(w, h, "\n  ".join(parts), css)


def build_hero():
    w, h = 650, 215
    rnd = random.Random(7)
    stars = []
    for _ in range(60):
        sx, sy = rnd.uniform(0, w), rnd.uniform(0, h * 0.75)
        r = rnd.uniform(0.4, 1.4)
        stars.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" fill="#dbe4ff" '
                     f'opacity="{rnd.uniform(0.15, 0.7):.2f}"/>')
    body = f'''<defs>
    <linearGradient id="sky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#0d1117"/>
    </linearGradient>
    <linearGradient id="hero" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#a78bfa"/><stop offset="1" stop-color="#22d3ee"/>
    </linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="#f5f5dc" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#f5f5dc" stop-opacity="0"/></radialGradient>
  </defs>
  {rect(0.5, 0.5, w - 1, h - 1, "url(#sky)", rx=12, stroke=CARD_BORDER)}
  {''.join(stars)}
  <circle cx="562" cy="52" r="34" fill="url(#glow)"/>
  <circle cx="562" cy="52" r="17" fill="#f0f0d8"/>
  <path d="M330 {h - 1} L440 {h - 78} L500 {h - 30} L560 {h - 95} L650 {h - 1} Z" fill="#111b2e" opacity="0.9"/>
  <path d="M300 {h - 1} L400 {h - 46} L470 {h - 12} L540 {h - 58} L650 {h - 20} L650 {h - 1} Z" fill="#0a1322"/>
  {text(24, 44, "> Hey, I'm", size=14, fill=MUTED, family=MONO)}
  {text(24, 102, "ASHIS", size=54, fill="url(#hero)", weight="800")}
  <text x="24" y="134" font-family="{FONT}" font-size="15.5" font-weight="700" fill="#ffffff">
    Full-Stack Developer <tspan fill="#22d3ee">| Software Engineer</tspan></text>
  {text(24, 160, "I build scalable web apps and turn ideas into real-world", size=11.5, fill=MUTED)}
  {text(24, 176, "products — from UI to API to deploy.", size=11.5, fill=MUTED)}
  {pill(24, 190, 158, "Open to Opportunities", dot=True)}
  {pill(190, 190, 146, "React · Next.js · Node.js")}
  {pill(344, 190, 64, "India")}
  <text x="470" y="150" font-family="'Segoe Script', 'Bradley Hand', cursive" font-size="15"
        fill="#9fb0c9" transform="rotate(-7 470 150)">Code. Create.</text>
  <text x="476" y="172" font-family="'Segoe Script', 'Bradley Hand', cursive" font-size="15"
        fill="#9fb0c9" transform="rotate(-7 476 172)">Contribute. Repeat.</text>'''
    css = PULSE_CSS
    return svg_doc(w, h, body, css)


def pill(x, y, w, label, dot=False):
    gap = 12 if dot else 0
    body = rect(x, y, w, 24, "#161b22", rx=12, stroke=CARD_BORDER)
    tx = x + w / 2 + gap / 2
    body += text(tx, y + 16, label, size=10.5, fill=TEXT, anchor="middle")
    if dot:
        body += (f'<circle cx="{x + 14}" cy="{y + 12}" r="5" fill="#3fb950" '
                 f'style="animation: pulse 1.8s ease-in-out infinite"/>')
    return body


def build_tech(icons):
    items = [
        ("typescript", "TypeScript"), ("react", "React"), ("nextdotjs", "Next.js"),
        ("nodedotjs", "Node.js"), ("tailwindcss", "Tailwind"), ("redux", "Redux"),
        ("mongodb", "MongoDB"), ("postgresql", "Postgres"),
        ("prisma", "Prisma"), ("firebase", "Firebase"), ("express", "Express"),
        ("docker", "Docker"), ("git", "Git"), ("vercel", "Vercel"), ("figma", "Figma"),
    ]
    w, h = 650, 158
    parts = [card(w, h)]
    parts.append(f'{text(18, 30, "</>", size=15, fill="#22d3ee", weight="800", family=MONO)}'
                 f'{text(52, 30, "Tech Stack", size=15, fill="#ffffff", weight="800")}')
    per_row = 8
    cell = (w - 36) / per_row
    for i, (slug, label) in enumerate(items):
        col, row = i % per_row, i // per_row
        cx = 18 + cell * col + cell / 2
        y = 52 + row * 52
        size = 24
        parts.append(f'<image href="data:image/svg+xml;base64,{icons[slug]}" x="{cx - size / 2:.1f}" '
                     f'y="{y}" width="{size}" height="{size}"/>')
        parts.append(text(f"{cx:.1f}", y + size + 14, label, size=9.5, fill=MUTED, anchor="middle"))
    return svg_doc(w, h, "\n  ".join(parts))


def build_stats(stats):
    w, h = 315, 150
    parts = [card(w, h)]
    parts.append(text(16, 30, "📊", size=13))
    parts.append(text(40, 30, "GitHub Stats", size=14.5, fill="#ffffff", weight="800"))
    cells = [
        (str(stats["repos"]), "Total Repositories"),
        (str(stats["commits"]), "Total Commits"),
        (str(stats["prs"]), "Pull Requests"),
        (str(stats["issues"]), "Issues Resolved"),
    ]
    for i, (value, label) in enumerate(cells):
        x = 16 + (i % 2) * 152
        y = 66 + (i // 2) * 46
        parts.append(text(x, y, value, size=19, fill=ACCENT, weight="800"))
        parts.append(text(x, y + 16, label, size=9.5, fill=MUTED))
    return svg_doc(w, h, "\n  ".join(parts))


def build_project(name, title, desc, tags, accent, letter):
    w, h = 315, 148
    parts = [card(w, h)]
    parts.append(rect(16, 16, 34, 34, accent, rx=9))
    parts.append(text(33, 39, letter, size=17, fill="#ffffff", weight="800", anchor="middle"))
    parts.append(text(60, 32, title, size=13.5, fill="#ffffff", weight="800"))
    parts.append(text(60, 47, f"github.com/{OWNER}", size=9, fill=MUTED))
    y = 74
    for line in wrap(desc, 46)[:2]:
        parts.append(text(16, y, line, size=10.5, fill=MUTED))
        y += 14
    x = 16
    for tag in tags:
        tw = len(tag) * 5.4 + 16
        parts.append(rect(x, 108, tw, 18, "#21262d", rx=9))
        parts.append(text(x + tw / 2, 121, tag, size=9, fill=TEXT, anchor="middle"))
        x += tw + 6
    parts.append(text(w - 16, 121, "Repo →", size=10.5, fill=ACCENT, anchor="end", weight="700"))
    return svg_doc(w, h, "\n  ".join(parts))


def build_heatmap(contrib):
    days = [d for week in contrib["weeks"] for d in week["contributionDays"]]
    days = days[-364:]
    total = contrib["totalContributions"]
    cell, gap, cols = 9, 2.5, 52
    grid_w = cols * (cell + gap)
    x0, y0 = 44, 58
    w = 650
    h = y0 + 7 * (cell + gap) + 40
    levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    parts = [card(w, h)]
    parts.append(text(16, 30, "🧭", size=13))
    parts.append(text(40, 30, "Contribution Activity", size=14.5, fill="#ffffff", weight="800"))
    parts.append(text(w - 16, 30, f"{total} contributions in the last year",
                      size=10.5, fill=MUTED, anchor="end"))
    by_date = {d["date"]: d["contributionCount"] for d in days}
    start = len(days) - cols * 7
    first = days[start]["date"] if start > 0 else days[0]["date"]
    import datetime
    d0 = datetime.date.fromisoformat(first)
    last_label = -99
    for c in range(cols):
        for r in range(7):
            dt = d0 + datetime.timedelta(days=c * 7 + r)
            if dt.isoformat() not in by_date:
                continue
            cnt = by_date[dt.isoformat()]
            lvl = 0 if cnt == 0 else 1 if cnt <= 1 else 2 if cnt <= 3 else 3 if cnt <= 5 else 4
            parts.append(rect(x0 + c * (cell + gap), y0 + r * (cell + gap), cell, cell,
                              levels[lvl], rx=2))
        week_date = d0 + datetime.timedelta(days=c * 7)
        if (c == 0 or week_date.day <= 7) and c - last_label >= 3:
            last_label = c
            parts.append(text(x0 + c * (cell + gap), y0 - 10, week_date.strftime("%b"),
                              size=9, fill=MUTED, anchor="middle"))
    for i, label in [(0, "Mon"), (2, "Wed"), (4, "Fri")]:
        parts.append(text(x0 - 10, y0 + i * (cell + gap) + 8, label, size=9, fill=MUTED, anchor="end"))
    legend_x = x0 + grid_w - 4 * (cell + gap) - 60
    legend_y = h - 16
    parts.append(text(legend_x, legend_y, "Less", size=9, fill=MUTED, anchor="end"))
    for i in range(5):
        parts.append(rect(legend_x + 8 + i * (cell + gap), legend_y - 8, cell, cell,
                          levels[i], rx=2))
    parts.append(text(legend_x + 8 + 5 * (cell + gap) + 6, legend_y, "More", size=9, fill=MUTED))
    return svg_doc(w, h, "\n  ".join(parts))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
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

    avatar_b64 = base64.b64encode(fetch(f"https://github.com/{OWNER}.png?size=400")).decode()
    icon_slugs = ["typescript", "react", "nextdotjs", "nodedotjs", "tailwindcss", "redux",
                  "mongodb", "postgresql", "prisma", "firebase", "express", "docker",
                  "git", "vercel", "figma"]
    colors = {"typescript": "3178C6", "react": "61DAFB", "nextdotjs": "FFFFFF",
              "nodedotjs": "5FA04E", "tailwindcss": "06B6D4", "redux": "764ABC",
              "mongodb": "47A248", "postgresql": "4169E1", "prisma": "FFFFFF",
              "firebase": "DD2C00", "express": "FFFFFF", "docker": "2496ED",
              "git": "F05032", "vercel": "FFFFFF", "figma": "F24E1E"}
    icons = {s: base64.b64encode(
        fetch(f"https://cdn.simpleicons.org/{s}/{colors[s]}")).decode() for s in icon_slugs}

    (OUT / "sidebar.svg").write_text(build_sidebar(avatar_b64), encoding="utf-8")
    (OUT / "hero.svg").write_text(build_hero(), encoding="utf-8")
    (OUT / "tech.svg").write_text(build_tech(icons), encoding="utf-8")
    (OUT / "stats.svg").write_text(build_stats(stats), encoding="utf-8")
    (OUT / "heatmap.svg").write_text(build_heatmap(contrib), encoding="utf-8")

    projects = [
        ("teen-helpline", "Teen Helpline",
         "Mental wellness platform — counselling booking, journal, mood tracking & community.",
         ["Next.js", "Prisma", "TypeScript"], "#3178C6", "T"),
        ("work-", "Employee Management",
         "MERN employee records app — full CRUD dashboard for teams.",
         ["React", "Node.js", "MongoDB"], "#F7DF1E", "W"),
        ("github-badges", "GitHub Badges",
         "Profile badges and README widget collection.",
         ["Markdown", "Badges"], "#8B5CF6", "B"),
        ("priv", "VEDAA Portfolio",
         "3D developer portfolio and profile README experiments.",
         ["TypeScript", "3D Web"], "#06B6D4", "P"),
    ]
    for name, title, desc, tags, accent, letter in projects:
        (OUT / f"proj-{name}.svg").write_text(
            build_project(name, title, desc, tags, accent, letter), encoding="utf-8")

    preview = ["<html><body style='background:#010409;width:960px;margin:0 auto;font-family:sans-serif'>"]
    preview.append("<div style='display:flex;gap:14px'>")
    preview.append(f"<div style='width:260px'><img src='assets/dash/sidebar.svg' style='width:100%'></div>")
    preview.append("<div style='flex:1'>")
    for f in ["hero", "tech"]:
        preview.append(f"<img src='assets/dash/{f}.svg' style='width:100%;margin-bottom:14px'>")
    preview.append("<div style='display:flex;gap:14px;margin-bottom:14px'>"
                   "<img src='assets/dash/stats.svg' style='width:49%'>"
                   "<img src='https://streak-stats.demolab.com?user=ashis2489&theme=github-dark-blue"
                   "&hide_border=true&background=0D1117&ring=00F2FE&fire=FF6B35&stroke=0d1117'"
                   " style='width:49%'></div>")
    for pair in [("teen-helpline", "work-"), ("github-badges", "priv")]:
        preview.append("<div style='display:flex;gap:14px;margin-bottom:14px'>")
        for name in pair:
            preview.append(f"<img src='assets/dash/proj-{name}.svg' style='width:49%'>")
        preview.append("</div>")
    preview.append("<img src='assets/dash/heatmap.svg' style='width:100%'>")
    preview.append("</div></div></div></body></html>")
    pathlib.Path("preview.html").write_text("\n".join(preview), encoding="utf-8")
    print("generated:", *[p.name for p in sorted(OUT.glob("*.svg"))], "| stats:", stats)


if __name__ == "__main__":
    main()
