#!/usr/bin/env python3
"""
Convert cv.md (the source of truth) into resume.json (consumed by template.typ).

You edit cv.md. This script regenerates resume.json. The GitHub Action runs it
automatically before compiling the PDF; locally, run `python build.py`.

cv.md conventions
-----------------
- YAML frontmatter holds header/contact fields.
- A blockquote (> ...) right after the frontmatter is the summary.
- `## Section` starts a section: Experience, Education, Skills, Languages.
- Experience/Education entries:  `### Title @ Organization`
      *start – end* · optional note        (dates line, en dash between them;
                                             "present"/"now" => ongoing)
      one or more paragraph lines           -> entry summary
      - bullet lines                        -> highlights
  For education, the Title is split on the first comma into degree, field.
- Bold lead-in: text before the first ": " in a bullet is rendered bold, so
  writing `- **Label:** text` looks good both on GitHub and in the PDF.
"""

import json
import re
import sys
import pathlib

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("cv.md")
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path("resume.json")

ONGOING = {"present", "now", "current", "ongoing", ""}


def strip_inline(s: str) -> str:
    """Remove markdown emphasis markers, keeping the text content."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)     # **bold**
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"\1", s)  # *italic*
    s = re.sub(r"`(.+?)`", r"\1", s)            # `code`
    return s.strip()


def split_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit("cv.md must start with a YAML frontmatter block delimited by ---")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def parse_dateline(line: str):
    """`*2024-01 – present* · Full-time` -> ('2024-01', '', 'Full-time')."""
    m = re.match(r"\*(.+?)\*(?:\s*·\s*(.+))?$", line.strip())
    if not m:
        return None
    span, note = m.group(1), (m.group(2) or "").strip()
    # Split only on a dash surrounded by whitespace (the range separator),
    # so hyphens inside ISO dates like "2024-01" are preserved.
    parts = re.split(r"\s+[–—-]\s+", span.strip(), maxsplit=1)
    start = parts[0].strip()
    end = parts[1].strip() if len(parts) > 1 else ""
    if end.lower() in ONGOING:
        end = ""
    return start, end, note


def parse_entries(lines, is_education):
    entries = []
    cur = None
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("### "):
            if cur:
                entries.append(cur)
            title, _, org = line[4:].partition("@")
            cur = {"_title": title.strip(), "org": org.strip(),
                   "start": "", "end": "", "note": "", "logo": "",
                   "summary": [], "highlights": []}
        elif cur is None:
            continue
        elif line.strip().startswith("<!--"):
            m = re.search(r"logo:\s*(.+?)\s*-->", line)
            if m:
                cur["logo"] = m.group(1).strip()
        elif line.strip().startswith("*") and cur["start"] == "" and not cur["highlights"]:
            dl = parse_dateline(line)
            if dl:
                cur["start"], cur["end"], cur["note"] = dl
        elif line.strip().startswith("- "):
            cur["highlights"].append(strip_inline(line.strip()[2:]))
        elif line.strip():
            cur["summary"].append(strip_inline(line.strip()))
    if cur:
        entries.append(cur)

    out = []
    for e in entries:
        summary = " ".join(e["summary"]).strip()
        if is_education:
            degree, _, field = e["_title"].partition(",")
            out.append({
                "studyType": degree.strip(),
                "area": field.strip(),
                "institution": e["org"],
                "note": summary,           # thesis / description line
                "startDate": e["start"],
                "endDate": e["end"],
                "logo": e["logo"],
            })
        else:
            out.append({
                "position": e["_title"],
                "name": e["org"],
                "note": e["note"],
                "startDate": e["start"],
                "endDate": e["end"],
                "logo": e["logo"],
                "summary": summary,
                "highlights": e["highlights"],
            })
    return out


def parse_skills(lines):
    skills = []
    for line in lines:
        m = re.match(r"-\s*(.+?):\s*(.+)$", strip_inline(line.strip()))
        if m:
            skills.append({
                "name": m.group(1).strip(),
                "keywords": [k.strip() for k in m.group(2).split(",") if k.strip()],
            })
    return skills


def parse_languages(lines):
    text = " ".join(l.strip() for l in lines if l.strip())
    langs = []
    for chunk in re.split(r"\s*·\s*|\s*,\s*", text):
        m = re.match(r"(.+?)\s*\((.+?)\)", chunk.strip())
        if m:
            langs.append({"language": m.group(1).strip(), "fluency": m.group(2).strip()})
    return langs


def main():
    text = SRC.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    # Summary = first blockquote in the body.
    summary = ""
    qm = re.search(r"^>\s*(.+)$", body, re.M)
    if qm:
        summary = strip_inline(qm.group(1).strip())

    # Location "City, Country" -> {city, countryName}
    location = {}
    if fm.get("location"):
        city, _, country = str(fm["location"]).rpartition(",")
        if city:
            location = {"city": city.strip(), "countryName": country.strip()}
        else:
            location = {"city": country.strip()}

    profiles = []
    if fm.get("website"):
        profiles.append({"network": "Website", "url": fm["website"]})
    if fm.get("scholar"):
        profiles.append({"network": "Google Scholar", "url": fm["scholar"]})

    basics = {
        "name": fm.get("name", ""),
        "label": fm.get("label", ""),
        "email": fm.get("email", ""),
        "phone": str(fm.get("phone", "")),
        "url": fm.get("website", ""),
        "citizenship": fm.get("citizenship", ""),
        "photo": fm.get("photo", ""),
        "summary": summary,
        "location": location,
        "profiles": profiles,
    }

    # Split body into `## Section` blocks.
    sections = {}
    cur_name, cur_lines = None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if cur_name:
                sections[cur_name] = cur_lines
            cur_name, cur_lines = line[3:].strip().lower(), []
        elif cur_name:
            cur_lines.append(line)
    if cur_name:
        sections[cur_name] = cur_lines

    resume = {
        "basics": basics,
        "work": parse_entries(sections.get("experience", []), is_education=False),
        "education": parse_entries(sections.get("education", []), is_education=True),
        "skills": parse_skills(sections.get("skills", [])),
        "languages": parse_languages(sections.get("languages", [])),
    }

    OUT.write_text(json.dumps(resume, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT}  —  {len(resume['work'])} roles, "
          f"{len(resume['education'])} degrees, {len(resume['skills'])} skill groups, "
          f"{len(resume['languages'])} languages.")

    # Render the GitHub Pages landing page from the same data, if the
    # template is present. CI injects the page images afterwards.
    tpl = pathlib.Path("site/index.template.html")
    if tpl.exists():
        def esc(s):
            return (str(s).replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
        links = []
        if basics["email"]:
            links.append(f'<a href="mailto:{basics["email"]}">{esc(basics["email"])}</a>')
        if fm.get("website"):
            host = re.sub(r"^https?://", "", fm["website"]).rstrip("/")
            links.append(f'<a href="{fm["website"]}">{esc(host)}</a>')
        if fm.get("scholar"):
            links.append(f'<a href="{fm["scholar"]}">Google Scholar</a>')
        html = (tpl.read_text(encoding="utf-8")
                .replace("{{NAME}}", esc(basics["name"]))
                .replace("{{ROLE}}", esc(basics["label"]))
                .replace("{{FOOTER_LINKS}}", " ·\n    ".join(links)))
        pathlib.Path("site/index.html").write_text(html, encoding="utf-8")
        print("Wrote site/index.html")


if __name__ == "__main__":
    main()
