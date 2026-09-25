// Academic CV. Content comes from _data/cv.yml and _bibliography/papers.bib
// via bin/build.py (which writes cv/build/data.json). Edit the data, not this file.
// This file only controls the look.

#let d = json("build/data.json")
#let p = d.profile

// ---------------------------------------------------------------- style
#let accent = rgb(20, 50, 110)
#let muted = rgb(95, 95, 95)

#set document(title: "Curriculum Vitae — " + p.name, author: p.name)
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2cm),
  footer: context [
    #set text(8pt, fill: muted)
    #p.name #h(1fr) Last updated #d.updated #h(1fr) #counter(page).display("1 / 1", both: true)
  ],
)
#set text(font: "TeX Gyre Pagella", size: 10pt, lang: "en", number-type: "old-style")
#set par(leading: 0.62em, justify: false)
#show link: set text(fill: accent)

#show heading.where(level: 1): it => {
  v(6pt)
  block(sticky: true, width: 100%)[
    #set text(12pt, fill: accent, weight: "regular")
    #text(tracking: 0.06em, smallcaps(it.body))
    #v(-7pt)
    #line(length: 100%, stroke: 0.5pt + accent)
  ]
  v(1pt)
}
#show heading.where(level: 2): it => block(sticky: true, above: 8pt, below: 5pt)[
  #set text(10pt, fill: accent, weight: "regular", style: "italic")
  #it.body
]

// date | content rows
#let entries(rows) = grid(
  columns: (2.9cm, 1fr),
  column-gutter: 0.4em,
  row-gutter: 0.6em,
  ..rows.map(((l, r)) => (text(fill: muted, l), r)).flatten(),
)

#let authors(list) = list.map(a => if a.me { strong(a.name) } else { a.name }).join(", ")

#let pub(x) = {
  authors(x.authors)
  [, “#x.title,” ]
  if x.section == "preprint" {
    link("https://arxiv.org/abs/" + x.arxiv)[arXiv:#x.arxiv]
    if x.primaryclass != "" [ \[#x.primaryclass\]]
    [ (#x.year).]
  } else {
    emph(x.venue)
    if x.volume != "" [ *#x.volume*]
    if x.number != "" [(#x.number)]
    if x.pages != "" [, #x.pages]
    [ (#x.year).]
  }
  if x.doi != "" [ #link("https://doi.org/" + x.doi)[doi:#x.doi]]
  else if x.section != "preprint" and x.url != "" [ #link(x.url)[#x.url.replace(regex("^https?://"), "")]]
}

#let pub-list(items, start) = {
  let n = start
  let rows = ()
  for x in items {
    n += 1
    let label = if x.selected [$star$ \[#n\]] else [\[#n\]]
    rows.push((align(right, label), pub(x)))
  }
  grid(columns: (3.2em, 1fr), column-gutter: 0.6em, row-gutter: 0.6em, ..rows.flatten())
}

// ---------------------------------------------------------------- header
#align(center)[
  #text(24pt)[#p.name.split(" ").slice(0, -1).join(" ") #smallcaps(p.name.split(" ").last())] \
  #v(2pt)
  #text(fill: muted, tracking: 0.12em, smallcaps[Curriculum Vitae]) \
  #v(4pt)
  #link("mailto:" + p.email)[#p.email]
  #h(0.4em)·#h(0.4em)
  #link(p.website)[#p.website.replace("https://", "")]
  #h(0.4em)·#h(0.4em)
  #link("https://github.com/" + p.github)[github.com/#p.github]
  #h(0.4em)·#h(0.4em)
  #link("https://scholar.google.com/citations?user=" + p.scholar_id)[Google Scholar]
]

*Research interests.* #p.interests.enumerate().map(((i, x)) => if i == 0 { x } else { lower(x.first()) + x.slice(x.first().len()) }).join(", ").

= Employment
#entries(d.positions.map(x => (
  x.range,
  [#x.title, #if "unit" in x and x.unit != none [#x.unit, ]*#x.org*],
)))

= Education
#entries(d.education.map(x => (
  x.range,
  [
    *#x.degree*#if "note" in x [ (_#{x.note}_)], #x.institution \
    #if "extra" in x [#x.extra \ ]
    Thesis: #if "thesis_url" in x { link(x.thesis_url, emph(x.thesis)) } else { emph(x.thesis) } \
    Supervisors: #x.supervisors
  ],
)))

= Teaching Experience
#d.teaching.institution
#v(2pt)
#entries(d.teaching.courses.map(c => (
  c.term,
  [_#{c.course}_ (#c.level) --- #c.role, #c.details],
)))

= Students Mentored
#entries(d.students.map(s => (
  s.years,
  [#s.name, #s.level, #s.institution --- #s.topic#if "cosupervisors" in s [; co-supervised with #s.cosupervisors]],
)))

= Research Stays and Grants
#entries(d.stays.map(s => (s.range, s.text)))

= Publications
#text(9pt, fill: muted)[Reverse chronological order. Key publications are marked with $star$.]

== Peer-reviewed articles
#pub-list(d.publications.peer_reviewed, 0)

== Preprints
#pub-list(d.publications.preprints, d.publications.peer_reviewed.len())

= Contributions to International Conferences and Workshops

#let talk-rows(ts) = ts.map(t => (
  t.year,
  [“#if "video" in t { link(t.video, t.title) } else { t.title },”
   #if "event_url" in t { link(t.event_url, t.event) } else { t.event }, #t.place],
))

#for (kind, title) in (("invited", "Invited talks"), ("contributed", "Contributed talks"), ("poster", "Posters")) {
  let ts = d.talks_by_type.at(kind)
  if ts.len() > 0 [
    == #title
    #entries(talk-rows(ts))
  ]
}

#if d.events.len() > 0 [
  == Schools and hackathons attended
  #entries(d.events.map(e => (e.year, [#e.name#if "place" in e [, #e.place]])))
]

= Languages and Skills
#entries((("Languages", d.languages.join(" · ")),) + d.skills.map(s => (s.label, s.details)))
