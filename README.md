# saleh0694.github.io

My academic homepage ([al-folio](https://github.com/alshedivat/al-folio) v1), my PDF CV and my
[GitHub profile README](https://github.com/Saleh0694) are all generated from **two files**:

| What | Where | Used by |
|---|---|---|
| Positions, education, teaching, students, talks, events, software, languages, skills, bio | [`_data/cv.yml`](_data/cv.yml) | website, CV PDF, GitHub README |
| Publications | [`_bibliography/papers.bib`](_bibliography/papers.bib) | website, CV PDF, GitHub README |

Update one of them, push, and everything else follows.

## Common edits

- **New talk:** add an entry at the top of `talks:` in `_data/cv.yml` (`type:` is `invited`, `contributed`, `poster` or `seminar`).
- **New paper:** paste the BibTeX into `papers.bib` and add `cvsection = {peer-reviewed}` or `{preprint}`.
  Add `selected = {true}` to feature it on the home page, in the README and with a ★ in the CV.
  When a preprint gets published, change its `cvsection` and add `journal`, `volume`, `pages`, `doi`.
- **Hide something from one output:** add `hide_in: [cv]` (or `web`, `readme`) to the YAML entry.
- **CV layout:** [`cv/cv.typ`](cv/cv.typ) (Typst). **README layout:** [`bin/readme.md.j2`](bin/readme.md.j2).

## What happens on push

1. `.github/workflows/deploy.yml` runs `python bin/build.py cv` (Typst → `assets/pdf/cv.pdf`),
   builds the Jekyll site and publishes it to the `gh-pages` branch, which GitHub Pages serves.
2. The profile repo `Saleh0694/Saleh0694` has a daily workflow (also runnable by hand under
   *Actions → Update README → Run workflow*) that regenerates its README from this repo.

## Building locally (optional, all free)

```bash
pip install -r bin/requirements.txt
python bin/build.py cv                       # CV only  -> assets/pdf/cv.pdf
python bin/build.py readme --out /tmp/README.md

docker compose up                            # whole site -> http://localhost:8080
```

## Notes

- `assets/css/main.scss` shadows the al_folio_core gem's file only to set the accent colour.
- `_pages/legacy-*.html` redirect the old site's `research.html` and `blog.html`, so links shared before 2026 still work.
- The TeX Gyre Pagella fonts in `cv/fonts/` are under the GUST Font License (included).
