// ============================================================================
//  CV template  —  reads resume.json and renders the PDF.
//  You normally DON'T need to edit this file: change your content in
//  resume.json instead. Come here only to tweak design (colors, fonts,
//  spacing). The knobs you're most likely to touch are right below.
// ============================================================================

#let data = json("resume.json")

// ---- Design knobs -----------------------------------------------------------
#let accent      = rgb("#26415E")   // section rules, name, links (deep slate blue)
#let body-font   = "Libertinus Serif" // ships with Typst — always available
#let base-size   = 10pt
#let page-margin = (x: 1.7cm, y: 1.6cm)
// -----------------------------------------------------------------------------

#let months = (
  "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
  "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
)

// Format an ISO-ish date string ("2024-01", "2015") into a readable label.
// Empty / missing endDate becomes "Present".
#let fmt-date(d) = {
  if d == none or d == "" { return "Present" }
  let parts = str(d).split("-")
  if parts.len() >= 2 {
    months.at(parts.at(1), default: "") + " " + parts.at(0)
  } else {
    parts.at(0)
  }
}

#let daterange(start, end) = fmt-date(start) + " – " + fmt-date(end)

// A logo scaled to fit within a fixed box, right-aligned, so wide and tall
// logos share a consistent footprint in the margin.
#let logo-box(path) = box(width: 2.7cm, height: 0.9cm)[
  #align(right + horizon, image(path, fit: "contain", width: 100%, height: 100%))
]

// Highlight convention: text before the first ": " is emphasised.
#let render-highlight(s) = {
  if ": " in s {
    let parts = s.split(": ")
    strong(parts.at(0)) + ": " + parts.slice(1).join(": ")
  } else {
    s
  }
}

// ---- Document & page setup --------------------------------------------------
#set document(
  title: data.basics.name + " — CV",
  author: data.basics.name,
)
#set page(paper: "a4", margin: page-margin, numbering: none)
#set text(font: body-font, size: base-size, fill: rgb("#1a1a1a"), lang: "en")
#set par(justify: true, leading: 0.6em)
#show link: it => text(fill: accent, it)

// Section heading with a full-width accent rule beneath it.
#let section(title) = {
  v(0.7em)
  text(size: 11.5pt, weight: "bold", fill: accent, tracking: 0.4pt,
    upper(title))
  v(-0.35em)
  line(length: 100%, stroke: 0.6pt + accent)
  v(0.15em)
}

// ---- Header -----------------------------------------------------------------
#{
  let b = data.basics

  let loc = if "location" in b {
    (b.location.at("city", default: ""), b.location.at("countryName", default: ""))
      .filter(x => x != "").join(", ")
  } else { "" }

  let bits = ()
  if "email" in b and b.email != "" { bits.push(link("mailto:" + b.email, b.email)) }
  if "phone" in b and b.phone != "" { bits.push(b.phone) }
  if "url"   in b and b.url   != "" { bits.push(link(b.url, b.url.replace("https://", "").replace("http://", ""))) }
  if loc != "" { bits.push(loc) }
  if "citizenship" in b and b.citizenship != "" { bits.push(b.citizenship) }

  let text-block = {
    text(size: 25pt, weight: "bold", fill: accent, b.name)
    if "label" in b and b.label != "" {
      v(-0.2em)
      text(size: 11pt, fill: rgb("#555555"), b.label)
    }
    v(0.4em)
    set text(size: 9pt, fill: rgb("#444444"))
    bits.join([  #text(fill: accent)[•]  ])
  }

  let has-photo = "photo" in b and b.photo != ""
  if has-photo {
    grid(columns: (1fr, auto), column-gutter: 1.2em, align: (left + horizon, right),
      text-block,
      box(radius: 5pt, clip: true, image(b.photo, width: 2.8cm)),
    )
  } else {
    text-block
  }
}

// ---- Summary ----------------------------------------------------------------
#if "summary" in data.basics and data.basics.summary != "" {
  v(0.6em)
  text(style: "italic", data.basics.summary)
}

// ---- Experience -------------------------------------------------------------
#if "work" in data and data.work.len() > 0 {
  section("Experience")
  for job in data.work {
    // Row: position + org on the left, dates on the right.
    grid(columns: (1fr, auto), column-gutter: 1em,
      {
        text(weight: "bold", size: 10.5pt, job.position)
        if "note" in job and job.note != "" {
          text(size: 8.5pt, fill: rgb("#777777"), "  (" + job.note + ")")
        }
        linebreak()
        text(fill: accent, job.name)
      },
      {
        align(right, text(size: 9pt, fill: rgb("#666666"),
          daterange(job.at("startDate", default: ""), job.at("endDate", default: ""))))
        if "logo" in job and job.logo != "" {
          v(3pt)
          align(right, logo-box(job.logo))
        }
      }
    )
    if "summary" in job and job.summary != "" {
      v(0.15em)
      text(size: 9.5pt, job.summary)
    }
    if "highlights" in job and job.highlights.len() > 0 {
      v(0.2em)
      set text(size: 9.5pt)
      list(indent: 0.4em, spacing: 0.5em,
        ..job.highlights.map(h => render-highlight(h)))
    }
    v(0.6em)
  }
}

// ---- Education --------------------------------------------------------------
#if "education" in data and data.education.len() > 0 {
  section("Education")
  for ed in data.education {
    grid(columns: (1fr, auto), column-gutter: 1em,
      {
        text(weight: "bold", ed.studyType)
        if "area" in ed and ed.area != "" { text(", " + ed.area) }
        linebreak()
        text(fill: accent, ed.institution)
        if "note" in ed and ed.note != "" {
          linebreak()
          text(size: 9pt, style: "italic", fill: rgb("#555555"), ed.note)
        }
      },
      {
        align(right, text(size: 9pt, fill: rgb("#666666"),
          daterange(ed.at("startDate", default: ""), ed.at("endDate", default: ""))))
        if "logo" in ed and ed.logo != "" {
          v(3pt)
          align(right, logo-box(ed.logo))
        }
      }
    )
    v(0.5em)
  }
}

// ---- Skills -----------------------------------------------------------------
#if "skills" in data and data.skills.len() > 0 {
  section("Skills")
  set text(size: 9.5pt)
  for sk in data.skills {
    grid(columns: (5.6cm, 1fr), column-gutter: 0.6em, row-gutter: 0.4em,
      text(weight: "bold", fill: accent, sk.name),
      sk.at("keywords", default: ()).join(", "),
    )
    v(0.25em)
  }
}

// ---- Languages --------------------------------------------------------------
#if "languages" in data and data.languages.len() > 0 {
  section("Languages")
  set text(size: 9.5pt)
  data.languages
    .map(l => l.language + " (" + l.fluency + ")")
    .join([   #text(fill: accent)[•]   ])
}

// ---- Publications link ------------------------------------------------------
#{
  let scholar = data.basics.at("profiles", default: ())
    .filter(p => p.at("network", default: "") == "Google Scholar")
  if scholar.len() > 0 {
    section("Publications")
    set text(size: 9.5pt)
    [Full and up-to-date list of publications available on ]
    link(scholar.at(0).url)[Google Scholar]
    [.]
  }
}
