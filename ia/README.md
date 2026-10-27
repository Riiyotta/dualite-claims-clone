# Dualite Claims — information architecture

`ia.json` is the only file to hand-edit. `IA.md` and `matrix.csv` are **generated** — never edit them; they are overwritten.

```bash
node validate.mjs && node build.mjs
```

Sources: route list from the original's `sitemap.xml`; home sections from the clone's `src/components/*.jsx` (each has `implementedBy`); blog index and article sections from the live original's markup. Blog templates have no `implementedBy` because the clone does not build them yet (its dev server answers `/blog/*` with the homepage).

## Findings

- 16 routes, 3 templates. 14 of the 16 routes (88%) are blog articles from one template, but the clone has built only the 1 home route. The 15 remaining routes need two templates: blog index and blog article.
- 5 sections are shared across all 3 templates: skip link, scroll progress, nav, mobile menu and footer. Those are the real shared components. The other 24 sections are single-template and should stay page-local.
- The preloader (`shell.loader`) and grain overlay (`shell.grain`) appear on the home route only. The blog pages on the original carry neither, so a blog build must not mount them.
- The home page is one long template of 20 sections; 13 of them are numbered content bands (01–11) plus the hero and the proof strip. All 13 are home-only.
