# CV

My CV, written in Markdown and rendered to a polished PDF with
[Typst](https://typst.app). Every push rebuilds the PDF and publishes a web
version to GitHub Pages.

**You edit one file: [`cv.md`](cv.md).** Everything else is generated.

```
cv.md  ──(build.py)──▶  resume.json  ──(Typst)──▶  CV_Hadi_Zaatiti.pdf
   ▲                          │
   │                          └──(build.py)──▶  site/index.html  (clickable web CV)
   └── the only file you edit
```

The website is a real HTML page with selectable text and working links (not an
image of the PDF). The downloadable PDF is named automatically from your name,
e.g. `CV_Hadi_Zaatiti.pdf`. Date ranges read as "Jan 2024 to Present"; to use a
dash instead, change the one `daterange` line in `template.typ`.

## How it fits together

| File | Role | Edit? |
|------|------|-------|
| `cv.md` | Your CV content (Markdown + a little YAML) | ✏️ **Yes** |
| `template.typ` | Layout & styling of the PDF | Rarely (design tweaks) |
| `build.py` | Turns `cv.md` into `resume.json` | No |
| `resume.json` | Generated data the template reads | No (auto-generated) |
| `site/index.template.html` | Web page shell | Rarely |
| `.github/workflows/deploy.yml` | Builds & deploys on every push | No |

## One-time setup

1. Create a new **public** GitHub repository named **`CV`** and push these files
   to the `main` branch.
2. In the repo: **Settings → Pages → Build and deployment → Source →
   GitHub Actions**.
3. Push any change (or run the workflow manually from the **Actions** tab).
   When it finishes, your CV is live at
   **`https://<your-username>.github.io/CV/`** with a Download-PDF button.

## Editing your CV

Open `cv.md`, change the text, commit, push. That's it — the PDF and website
rebuild automatically. `cv.md` also renders nicely on GitHub, so it doubles as a
readable plain-text CV.

### Format rules for `cv.md`

- **Header / contact** live in the YAML block at the top (between the `---`
  lines): `name`, `label`, `affiliation`, `email`, `phone`, `website`,
  `location`, `citizenship`, `age`, `caption`, `scholar`, `photo`. In the PDF
  these fill the bordered contact box (with icons from `images/icons/`), the
  name, and the photo + caption, matching the original three-column header.
- The **`>` blockquote** right after the header is your summary.
- **`## Experience`** and **`## Education`** hold entries shaped like:

  ```markdown
  ### Job Title @ Organization
  *2022-02 – 2024-01* · Full-time

  A short optional description paragraph.

  - **Lead-in:** a highlight. Text before the first colon is shown in bold.
  ```

  Dates are `YYYY-MM` or `YYYY`. Use `present` for an ongoing role. In
  `## Education`, the title before `@` is split on the first comma into
  *degree, field* (e.g. `Master of Engineering, Embedded Systems`).
- **`## Skills`** — one `- **Group:** item, item, item` line per group.
- **`## Languages`** — `English (Advanced) · French (Fluent)`.

## Previewing locally (optional)

You don't need this — GitHub builds everything for you — but if you want a live
preview while editing:

```bash
pip install pyyaml
python build.py            # cv.md -> resume.json (+ site/index.html)

# Install Typst once: https://github.com/typst/typst#installation
typst watch template.typ cv.pdf   # live-recompiles the PDF as you save
```

Note: after editing `cv.md` you must re-run `python build.py` to regenerate
`resume.json` before Typst picks up the change.

## Photo & logos

Your portrait and the institution logos were extracted from your original PDF
and live in `images/`:

- `images/photo.jpg` — shown top-right of the header. Set or change it via the
  `photo:` field in the `cv.md` frontmatter (remove the line to drop the photo).
- `images/logos/` — one logo per file (`nyuad.png`, `airbus.png`, `systemx.png`,
  `stanford-inria.png`, `cea.png`, `centralesupelec.png`, `paris-saclay.png`,
  `lebanese-university.png`, plus a few `extra-*` odds and ends).

To place a logo beside an entry, add a hidden comment right under its heading in
`cv.md` (invisible when the Markdown is viewed on GitHub):

```markdown
### Research Scientist @ New York University, Abu Dhabi
<!-- logo: images/logos/nyuad.png -->
*2024-01 – present* · Full-time
```

Swap the filename to use a different logo, or delete the comment for no logo.

## Changing the design

Open `template.typ`. The knobs you're most likely to touch are grouped at the
top: `accent` colour, `body-font`, base font size and page margins. The default
font (Libertinus Serif) ships with Typst, so it always works. To use another
font, install it in the workflow or switch to a Google Font in your local setup.
