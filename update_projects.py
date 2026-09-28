import json
import os
import pathlib
import re

repos = json.load(open(os.environ.get("REPOS_JSON", "/tmp/repos.json")))
profile = os.environ.get("PROFILE", "")

rows = []
for r in repos:
    if r["fork"] or r["name"].startswith(".") or r["name"] == profile or r["size"] <= 0:
        continue
    line = f"- [{r['name']}]({r['html_url']})"
    if r.get("language"):
        line += f" — {r['language']}"
    if r.get("description"):
        line += f" · {r['description']}"
    rows.append(line)
    if len(rows) == 5:
        break

readme = pathlib.Path("README.md")
text = readme.read_text(encoding="utf-8")
text = re.sub(
    r"<!--PROJECTS:START-->.*?<!--PROJECTS:END-->",
    "<!--PROJECTS:START-->\n" + "\n".join(rows) + "\n<!--PROJECTS:END-->",
    text,
    flags=re.S,
)
readme.write_text(text, encoding="utf-8")
print("\n".join(rows) or "no repos matched")
