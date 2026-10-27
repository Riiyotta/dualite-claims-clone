# https://claims.dualite.dev/ (clone at clone/src)

Source: https://claims.dualite.dev/ (clone at clone/src)
Status: **measured-from-live-and-clone** · production approved: **false**
16 routes · 3 templates · 29 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 3 templates (Blog article, Home, Blog index) account for 16 of 16 routes (100%). The remaining 0 routes span 0 templates.

| template | routes | share |
|---|---:|---:|
| Blog article | 14 | 88% |
| Home | 1 | 6% |
| Blog index | 1 | 6% |

## Page chrome

**16 routes carry chrome = `unspecified`** — Home, Blog index, Blog article.

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `shell.skip-link` | SHELL | 3 | 16 | `src/components/Skip.jsx` | All 16 routes. |
| `shell.scroll-progress` | SHELL | 3 | 16 | `src/components/Progress.jsx` | All 16 routes. |
| `shell.nav` | SHELL | 3 | 16 | `src/components/Nav.jsx` | All 16 routes. |
| `shell.mobile-menu` | SHELL | 3 | 16 | `src/components/Mmenu.jsx` | All 16 routes. |
| `shell.footer` | SHELL | 3 | 16 | `src/components/Footer.jsx` | All 16 routes. |
| `editorial.breadcrumbs` | EDITORIAL | 1 | 14 | _not yet built_ | All 14 article routes. |
| `editorial.post-header` | EDITORIAL | 1 | 14 | _not yet built_ | All 14 article routes. |
| `editorial.post-toc` | EDITORIAL | 1 | 14 | _not yet built_ | All 14 article routes. |
| `editorial.post-body` | EDITORIAL | 1 | 14 | _not yet built_ | All 14 article routes. |
| `editorial.post-cta` | EDITORIAL | 1 | 14 | _not yet built_ | All 14 article routes. |
| `editorial.related-posts` | EDITORIAL | 1 | 14 | _not yet built_ | All 14 article routes. |
| `shell.loader` | SHELL | 1 | 1 | `src/components/Loader.jsx` | Home route only (1 route). |
| `shell.grain` | SHELL | 1 | 1 | `src/components/Grain.jsx` | Home route only (1 route). |
| `hero.home` | HERO | 1 | 1 | `src/components/Hero.jsx` | Home route only (1 route). |
| `proof.quote-strip` | PROOF | 1 | 1 | `src/components/Proof.jsx` | Home route only. |
| `proof.results` | PROOF | 1 | 1 | `src/components/Results.jsx` | Home route only. |
| `proof.customer-story` | PROOF | 1 | 1 | `src/components/Story.jsx` | Home route only. |
| `proof.case-study` | PROOF | 1 | 1 | `src/components/Case.jsx` | Home route only. |
| `features.problem` | FEATURES | 1 | 1 | `src/components/Problem.jsx` | Home route only. |
| `features.movement` | FEATURES | 1 | 1 | `src/components/Move.jsx` | Home route only. |
| `features.product-demo` | FEATURES | 1 | 1 | `src/components/Demo.jsx` | Home route only. |
| `features.platform` | FEATURES | 1 | 1 | `src/components/Platform.jsx` | Home route only. |
| `features.trust` | FEATURES | 1 | 1 | `src/components/Trust.jsx` | Home route only. |
| `features.reconciliation` | FEATURES | 1 | 1 | `src/components/Recon.jsx` | Home route only. |
| `support.faq` | SUPPORT | 1 | 1 | `src/components/Faq.jsx` | Home route only. |
| `conversion.demo-form` | CONVERSION | 1 | 1 | `src/components/Cta.jsx` | Home route only. |
| `editorial.blog-hero` | EDITORIAL | 1 | 1 | _not yet built_ | Blog index only (1 route). |
| `editorial.featured-post` | EDITORIAL | 1 | 1 | _not yet built_ | Blog index only (1 route). |
| `editorial.post-list` | EDITORIAL | 1 | 1 | _not yet built_ | Blog index only (1 route). |

**5 shared sections** appear in more than one template and belong in a component library.

**24 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

**9 sections have no `implementedBy` yet** — not necessarily missing, just not linked to a component in this pass: `editorial.breadcrumbs`, `editorial.post-header`, `editorial.post-toc`, `editorial.post-body`, `editorial.post-cta`, `editorial.related-posts`, `editorial.blog-hero`, `editorial.featured-post`, `editorial.post-list`.

## Templates

### Home — `template.home`

1 route · `/`

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×3 |
| 2 | SHELL | `shell.loader` | page-local |
| 3 | SHELL | `shell.scroll-progress` | shared ×3 |
| 4 | SHELL | `shell.grain` | page-local |
| 5 | SHELL | `shell.nav` | shared ×3 |
| 6 | SHELL | `shell.mobile-menu` | shared ×3 |
| 7 | HERO | `hero.home` | page-local |
| 8 | PROOF | `proof.quote-strip` | page-local |
| 9 | FEATURES | `features.problem` | page-local |
| 10 | PROOF | `proof.results` | page-local |
| 11 | FEATURES | `features.movement` | page-local |
| 12 | FEATURES | `features.product-demo` | page-local |
| 13 | FEATURES | `features.platform` | page-local |
| 14 | FEATURES | `features.trust` | page-local |
| 15 | FEATURES | `features.reconciliation` | page-local |
| 16 | PROOF | `proof.customer-story` | page-local |
| 17 | PROOF | `proof.case-study` | page-local |
| 18 | SUPPORT | `support.faq` | page-local |
| 19 | CONVERSION | `conversion.demo-form` | page-local |
| 20 | SHELL | `shell.footer` | shared ×3 |

### Blog index — `template.blog-index`

1 route · `/blog/`

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×3 |
| 2 | SHELL | `shell.scroll-progress` | shared ×3 |
| 3 | SHELL | `shell.nav` | shared ×3 |
| 4 | SHELL | `shell.mobile-menu` | shared ×3 |
| 5 | EDITORIAL | `editorial.blog-hero` | page-local |
| 6 | EDITORIAL | `editorial.featured-post` | page-local |
| 7 | EDITORIAL | `editorial.post-list` | page-local |
| 8 | SHELL | `shell.footer` | shared ×3 |

### Blog article — `template.blog-post`

14 routes · `/blog/rghs-claim-submission-guide/`, `/blog/rghs-ipd-claim-submission/`, `/blog/rghs-opd-claim-submission/`, `/blog/rghs-claim-rejection-reasons/`, `/blog/echs-claim-submission-guide/`, `/blog/echs-ipd-claim-submission/`, `/blog/echs-opd-claim-submission/`, `/blog/echs-claim-rejection-reasons/`, `/blog/cghs-claim-submission-guide/`, `/blog/maa-yojana-claim-process-hospitals/`, `/blog/pmjay-claim-submission-tms/`, `/blog/hospital-claim-desk-problems/`, `/blog/medipulse-hospital-claims-automation/`, `/blog/how-dualite-claims-works/`

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×3 |
| 2 | SHELL | `shell.scroll-progress` | shared ×3 |
| 3 | SHELL | `shell.nav` | shared ×3 |
| 4 | SHELL | `shell.mobile-menu` | shared ×3 |
| 5 | EDITORIAL | `editorial.breadcrumbs` | page-local |
| 6 | EDITORIAL | `editorial.post-header` | page-local |
| 7 | EDITORIAL | `editorial.post-toc` | page-local |
| 8 | EDITORIAL | `editorial.post-body` | page-local |
| 9 | EDITORIAL | `editorial.post-cta` | page-local |
| 10 | EDITORIAL | `editorial.related-posts` | page-local |
| 11 | SHELL | `shell.footer` | shared ×3 |

## Section reference

### SHELL

_Site chrome and runtime utility UI: skip link, preloader, scroll progress, grain overlay, navigation, mobile menu, footer._

**`shell.skip-link`** — Visually hidden 'Skip to content' link targeting #main.

· All 16 routes. · appears on 16 routes · implemented by `src/components/Skip.jsx`

**`shell.loader`** — Full-screen intro preloader: brand label and claim-file tag, drawn seal SVG with ring text and checkmark, status line, 00 to 100 counter, progress bar, six-panel exit wipe. Plays once per session.

· Home route only (1 route). · appears on 1 routes · implemented by `src/components/Loader.jsx`

**`shell.scroll-progress`** — Fixed thin bar at the top of the viewport that fills with page scroll progress.

· All 16 routes. · appears on 16 routes · implemented by `src/components/Progress.jsx`

**`shell.grain`** — Fixed full-viewport animated film-grain texture overlay.

· Home route only (1 route). · appears on 1 routes · implemented by `src/components/Grain.jsx`

**`shell.nav`** — Fixed top navigation: logo and 'Claims' wordmark, six primary links with roll hover, magnetic 'Book a demo' button, burger on mobile. Hides on scroll down, switches theme over dark sections.

· All 16 routes. · appears on 16 routes · implemented by `src/components/Nav.jsx`

**`shell.mobile-menu`** — Dark full-screen mobile menu revealed by clip-path: numbered links, lime demo button, contact email.

· All 16 routes. · appears on 16 routes · implemented by `src/components/Mmenu.jsx`

**`shell.footer`** — Dark footer: oversized split-letter brand mark, link columns including blog guides, contact and legal line.

· All 16 routes. · appears on 16 routes · implemented by `src/components/Footer.jsx`

### HERO

_Page-opening composition._

**`hero.home`** — Home hero: scrambled eyebrow and status ticker, serif headline 'Scan the file. We'll handle the claim.', lede, primary and video CTAs, animated isometric claim-desk SVG scene, spec strip.

· Home route only (1 route). · appears on 1 routes · implemented by `src/components/Hero.jsx`

### PROOF

_Social proof: customer quote strip, outcome stats, customer story, case study._

**`proof.quote-strip`** — Customer proof strip with a scroll-scrubbed quote directly under the hero.

· Home route only. · appears on 1 routes · implemented by `src/components/Proof.jsx`

**`proof.results`** — (02) Dark results band 'Same claims. A lighter desk.' with odometer and counter stats.

· Home route only. · appears on 1 routes · implemented by `src/components/Results.jsx`

**`proof.customer-story`** — (08) Dark 'In his own words.' customer testimonial video with custom cursor.

· Home route only. · appears on 1 routes · implemented by `src/components/Story.jsx`

**`proof.case-study`** — (09) Case study teaser: a hospital cutting its claim backlog from a week to three days.

· Home route only. · appears on 1 routes · implemented by `src/components/Case.jsx`

### FEATURES

_Product explanation: the problem, workflow, product demo, capabilities, trust/accuracy, reconciliation._

**`features.problem`** — (01) The claim-desk problem: cost breakdown of manual filing.

· Home route only. · appears on 1 routes · implemented by `src/components/Problem.jsx`

**`features.movement`** — (03) 'Scan and forget.' pinned, scroll-scrubbed walkthrough of a claim file moving through the steps.

· Home route only. · appears on 1 routes · implemented by `src/components/Move.jsx`

**`features.product-demo`** — (04) 'One claim batch, start to finish.' stepped interactive product demo with auto-cycle and step buttons.

· Home route only. · appears on 1 routes · implemented by `src/components/Demo.jsx`

**`features.platform`** — (05) 'Three capabilities. No re-work.' tabbed capability panel (validate, stamp, watch) with auto-advancing tabs and screenshots.

· Home route only. · appears on 1 routes · implemented by `src/components/Platform.jsx`

**`features.trust`** — (06) 'Measured twice. Filed once.' accuracy and human-approval section with an in-view looping video.

· Home route only. · appears on 1 routes · implemented by `src/components/Trust.jsx`

**`features.reconciliation`** — (07) Payment reconciliation: stuck money, deductions, spreadsheet replacement, with animated reconciliation rows.

· Home route only. · appears on 1 routes · implemented by `src/components/Recon.jsx`

### CONVERSION

_Lead capture and demo booking._

**`conversion.demo-form`** — (11) Dark demo-booking band with a lead form, inline validation and a thank-you state.

· Home route only. · appears on 1 routes · implemented by `src/components/Cta.jsx`

### SUPPORT

_Objection handling: FAQ._

**`support.faq`** — (10) 'Questions hospitals ask us.' non-exclusive accordion.

· Home route only. · appears on 1 routes · implemented by `src/components/Faq.jsx`

### EDITORIAL

_Blog index and article content._

**`editorial.blog-hero`** — Blog index header introducing the claims guides.

· Blog index only (1 route). · appears on 1 routes

**`editorial.featured-post`** — One large featured post card.

· Blog index only (1 route). · appears on 1 routes

**`editorial.post-list`** — Grid of post cards for every article.

· Blog index only (1 route). · appears on 1 routes

**`editorial.breadcrumbs`** — Breadcrumb trail back to the blog index.

· All 14 article routes. · appears on 14 routes

**`editorial.post-header`** — Article title, standfirst and metadata.

· All 14 article routes. · appears on 14 routes

**`editorial.post-toc`** — Sticky table of contents sidebar for the article.

· All 14 article routes. · appears on 14 routes

**`editorial.post-body`** — Long-form prose body of the article.

· All 14 article routes. · appears on 14 routes

**`editorial.post-cta`** — Aside promoting a demo from inside an article.

· All 14 article routes. · appears on 14 routes

**`editorial.related-posts`** — Three related post cards at the end of an article.

· All 14 article routes. · appears on 14 routes
