Source: https://claims.dualite.dev/

# Dualite Claims: clone spec (measured live, 2026-10-27)

Single route `/`, one long page. All values below come from a live Chromium run (Playwright 1.63, separate isolated contexts at 1440x900 DPR1 and 375x812 DPR2 `isMobile`/`hasTouch`), using `getComputedStyle`, `getBoundingClientRect`, `ScrollTrigger.getAll()` and network capture. Box notation is `[x, documentY, width, height]` in CSS px, measured at scrollY=0 after the intro finished. Elements that have a pending "once" reveal still carry their start transform (y +70/+24/+50/+60), so their boxes read that much lower until revealed. Section boxes are never transformed, so they are exact.

A parity run of the same script against the clone (http://localhost:5188) matched on every point: section boxes, docH, all 77 ScrollTriggers (start/end/pin/scrub), typography roles, hover/magnetic, FAQ, tabs, product demo cycle, mobile menu, loader timing and session gating. Only timing jitter (a few ms or px) differed. Use the numbers below as the regression baseline.

---

## 0. Global

### Document
| | 1440x900 | 375x812 |
|---|---|---|
| `scrollHeight` (pin-spacer included) | **17626** | **21028** |
| ScrollTrigger count | 77 | 77 |
| `html` class after boot | `js is-ready lenis` | same |
| `html` class on 2nd load in same session | `js no-loader lenis is-ready` | same |

Body: bg `#F5F0E6` (rgb 245,240,230), color `#1E2318`, `Geist` 16.128px/24.9984px (desktop; `--fs-body` clamp gives 15px/23.25px at 375).

### Design tokens (`:root`, computed)
`--paper #F5F0E6` · `--paper-2 #EFE8D8` · `--paper-3 #E8DFCB` · `--card #FFFDF8` · `--ink #1E2318` · `--ink-2 #464B3A` · `--muted #6A6E5B` · `--faint #8A8C78` · `--line #DDD3BF` · `--line-2 #CFC4AB` · `--line-soft #EDE6D6` · `--olive #3D5A2A` · `--olive-2 #4E7A35` · `--olive-tint #E3EBD8` · `--night #1B2414` · `--night-2 #131A0E` · `--night-line #3B4A30` · `--lime #C5D69A` · `--on-night #F1ECDF` · `--on-night-2 #C9CBB6` · `--amber #B07A1E` · `--amber-ink #8A5A12`
Fonts: `--f-display 'Perfectly Nineties','Newsreader',Georgia,'Times New Roman',serif` · `--f-sans 'Geist',system-ui,-apple-system,'Segoe UI',sans-serif` · `--f-mono 'Geist Mono',ui-monospace,'SFMono-Regular',Menlo,monospace`
Scale: `--gutter clamp(20px,6.67vw,96px)` (96px at 1440, 25.0125px at 375) · `--maxw 1440px` · `--nav-h 76px` (64px at 375) · `--section-y clamp(96px,10vw,152px)` (section padding measured 144px desktop, 96px mobile) · `--fs-hero clamp(46px,6.3vw,98px)` · `--fs-h2 clamp(38px,4.45vw,68px)` · `--fs-h3 clamp(24px,2vw,30px)` · `--fs-lede clamp(17px,1.32vw,20px)` · `--fs-body clamp(15px,1.12vw,17px)` · `--ease-out cubic-bezier(.16,1,.3,1)` · `--ease-io cubic-bezier(.7,0,.2,1)`
Breakpoints (site.css): `max-width:1180px`, `980px` (JS `isDesktop = innerWidth > 980`), `820px`, `640px`, and `prefers-reduced-motion:reduce`.
GSAP eases: default `codex` = CustomEase `M0,0 C0.16,1 0.3,1 1,1`; `wipe` = `M0,0 C0.7,0 0.2,1 1,1`.

### Shared text roles (identical in every section)
| Role | Selector | 1440 | 375 |
|---|---|---|---|
| Section eyebrow | `span.eyebrow[data-scramble]` (+ `.eyebrow__idx` "(0N)") | Geist Mono 12px/18.6px, 400, ls 1.68px, uppercase, `#3D5A2A` (dark sections `#C5D69A`); idx `#8A8C78` (dark `rgb(124,135,102)`) | same |
| H2 | `h2.h2[data-split]` | Perfectly Nineties 64.08px/65.3616px, 400, ls -0.6408px, `#1E2318` (dark `#F1ECDF`). Exception: move h2 66.24px/67.5648px, ls -0.6624px | 38px/38.76px, ls -0.38px (move h2 34px/34.68px) |
| Lede | `p.lede` | Geist 19.008px/29.4624px, `#464B3A` (dark sections `#C9CBB6`) | 17px/26.35px |
| Body | `p.body` | Geist 16.128px/26.1274px, `#464B3A` | 15px/24.3px |
| Micro | `.micro` | Geist 13px/20.15px, `#6A6E5B` | same |
| Primary button | `a.btn.btn--primary` | Geist 16px/16px 500, white on `#3D5A2A`, h 56 (`--sm`: 15px, h 44, padding 0 20px); radius 0; border 1px transparent | same, full width 325 |
| Ghost button | `a.btn.btn--ghost` | Geist 16px 500, `#1E2318`, border 1px `rgb(189,177,149)`, h 56, padding 0 26px | full width |
| Text link | `a.link` | Geist 15px/23.25px, 2px bottom padding, underline = `linear-gradient(currentColor)` with `background-size:100% 1px` | same |

### Fixed chrome
- `.progress` fixed, z 120, `[0,0,1440,2]`; inner `span` bg `#4E7A35`, `scaleX` 0 to 1 scrubbed (scrub 0.3) over `start:0 → end:'max'`.
- `.grain` fixed, z 90, `2880x1800` at `[-749,-477]`, SVG `feTurbulence` data-URI background, keyframes `grain`.
- `.skip` link is the first child of body.

---

## 1. Loader `.loader` (fixed, z 150, padding 28px 96px / 28px 25px, bg `#F5F0E6`, display flex)

Structure: `.loader__top` (`<span>Dualite Claims</span><span class="loader__file">Claim 1187 · RGHS · OPD</span>`), `.loader__mid` (`svg.loader__seal` 132x132 viewBox with `circle.seal-ink` r62, 2x `circle.seal-draw` r62/r38 `pathLength=1000`, `text.seal-text` on `textPath href="#sealPath"` "DUALITE CLAIMS · CHECKED · SEALED · FILED ·" `textLength=292`, check `path.seal-draw` "M52 67l10 10 20-22" stroke-width 3), `.loader__bot` (`.loader__status`, `.loader__count`), `.loader__bar > span`, `.loader__panels` with **6** `<i>` (bg `#1B2414`, transform-origin 50% 100%).

Typography: `.loader__top`/`.loader__file` Geist Mono 11px/17.05px ls 1.54px uppercase `#6A6E5B`; `.loader__status` Geist Mono 12px/18.6px ls 1.68px uppercase `#3D5A2A`; `.loader__count` Perfectly Nineties **128px**/102.4px ls -2.56px `#6A6E5B` (375: 64px/51.2px ls -1.28px).

**Gating (head inline script, measured):** before CSS loads, `html.no-js` becomes `js`. If `sessionStorage['dc-intro']==='1'` or reduced motion, `no-loader` is added and the loader stays `display:none`. A 6000ms safety timer adds `no-loader` and removes `js` if `is-ready` never appears. Verified: first visit plays the loader; reload in the same context gives `html.js.no-loader…`, the loader `display:none`, and the hero intro runs immediately.

**Timeline (measured; T0 = moment `html` gets `is-ready`, which is after `document.fonts.ready` and is about 1134ms after navigation on a cold load):**
| T0 + ms | Event (measured values) |
|---|---|
| 0 | `lenis-stopped` on html; count "00", status "Opening claim file"; hero h1 words preset `translate(0,118%) rotate(3deg)` |
| 0 → 1250 (+160ms stagger per path) | `.seal-draw` stroke draws (dasharray "0 1010" → "1000 0"), ease inOut(3) |
| 0 → 1750 | counter 00→100 (2-digit pad), `.loader__bar span` scaleX 0→1, ease inOut(2); status changes at ≥22 "Reading 14 pages", ≥48 "Checking 50+ case rules", ≥74 "Applying Digistamp", ≥96 "Ready for review" (measured near 1711/1981/2253/2641ms abs) |
| 850 → 1450 | `.seal-text` opacity 0→1 (outQuad) |
| 1650 → 2170 | `.loader__seal` scale [1,.9,1.02,1], rotate 0→-8deg (rest: `rotate(-8deg) scale(1)`) |
| 1700 → 2120 | `.seal-ink` opacity 0→0.12, scale .6→1 |
| 2050 → ~2925 | panels `scaleY` 0→1, 650ms each, 55ms stagger, inOut(4) |
| 2780 | top/mid/bot/bar `visibility:hidden`, loader bg → transparent, **hero intro starts** (nav children opacity 0→1) |
| 2800 → ~3875 | panels `translateY 0 → -101%`, 800ms, 55ms stagger, inOut(4) |
| 3700 | loader `display:none`, `lenis.start()`, `sessionStorage['dc-intro']='1'` (measured: flag appears ~4830ms abs) |

## 2. Hero intro (GSAP timeline, ease expo.out; t=0 at loader reveal or immediately when `no-loader`)
`[data-hero]` autoAlpha 1 at 0 · `.nav__in > *` from y -24, autoAlpha 0, 1.2s, stagger .08 @0.1 · `.hero__guides i` from scaleY 0, 1.8s, stagger .07, expo.inOut @0 · `.hero__eyebrow` from y16/α0 1s @0.2 · h1 SplitText words (`.split-word`, mask words) to yPercent 0/rotate 0, 1.5s, stagger .055 @0.25 · `.hero__sub` from y26/α0/blur(10px) 1.4s @0.7 · `.hero__ctas > *` from y26/α0 1.2s stagger .09 @0.85 · `.hero__copy > .micro` α0 1s @1.1 · `.hero__scene` from y60/α0/scale .96 2s @0.35 · `.plate__corner` from scale 0, .9s, stagger .06, back.out(3) @1.0 · `.hero__foot > *` from y22/α0 1.1s stagger .07 @1.0 · status ticker @1.6.
Status ticker `[data-status]`: every 2800ms, ScrambleText (lowercase A-Z0-9 chars, speed .6, 0.9s) cycles "Reading discharge summary" → "Checking 50+ case rules" → "Collating 14 pages" → "Applying Digistamp" → "Draft saved on RGHS portal". Mid-scramble text such as "Collfua4xw7awrf05oik" is expected.

---

## 3. Nav `header#nav.nav` (fixed, z 100)
| | 1440 | 375 |
|---|---|---|
| box | `[0,0,1440,76]` | `[0,0,375,64]` |
| `.wrap.nav__in` | grid `363.562px 472.875px 363.562px`, gap 24px, padding 0 96px | grid `257px 44px`, gap 24px, padding 0 25px |
| `a.brand` | flex gap 14px `[96,27,206,22]`: `.brand__logo` (logo-dark.png + logo-light.png, both 92x22, natural 386x64), `.brand__rule`, `.brand__name` "Claims" Geist 14px/21.7px | `[25,21,206,22]` |
| `nav.nav__links` | flex gap 36px `[484,28,473,19]`; links Geist 15px/23.25px 400 `#1E2318`: How it works `#movement`, Platform `#platform`, Results `#results`, Trust `#trust`, FAQ `#faq`, Blog `/blog/` | hidden (0x0) |
| CTA | `a.btn.btn--primary.btn--sm[data-magnetic]` "Book a demo" `[1210,16,134,44]` | hidden |
| `.burger` | hidden | `[306,10,44,44]` display block, 2 spans |

States (measured):
- Top: bg transparent. `.is-scrolled` when y>12: bg `rgba(245,240,230,0.82)`, `border-bottom:1px solid rgba(207,196,171,0.6)`, `backdrop-filter:saturate(1.4) blur(14px)`.
- `.is-hidden` when y>240, direction down and velocity>40: `translateY(-76px)` (375: -64px). Removed on any upward scroll or y<240. Transition `transform .6s cubic-bezier(.7,0,.2,1), background-color .4s, color .4s, border-color .4s`.
- `.is-dark` while a `[data-theme=dark]` section (results, story, cta#demo, footer) crosses `top+=38`: bg `rgba(27,36,20,0.8)`, link color `#F1ECDF`.
- Active link: `aria-current="true"` while its section spans 45% of viewport height (triggers `top 45%`→`bottom 45%`).
- Anchor clicks (`a[href^="#"]`) are intercepted: `lenis.scrollTo(target,{duration:1.4})`; `#top` goes to y 0.

## 4. Mobile menu `#mmenu.mmenu[data-theme=dark]` (fixed, z 99, bg `#1B2414`, color `#F1ECDF`)
Padding 100px 96px 32px (375: 88px 25px 32px). `nav.mmenu__links` flex column gap 6px; 6 links `<a><span>0N</span>Label</a>` Perfectly Nineties 64px/67.2px at 1440, **41.25px/43.3125px at 375** (link boxes y 333/382/432/481/530/580, h 43). `.mmenu__foot` flex column gap 16px `[25,663,325,117]` holds `a.btn.btn--lime` "Book a 30-minute demo" (h 56, color `#1B2414`) and `a.micro` info@dualite.dev `rgb(159,165,140)`.
Behaviour (measured at 375): click `.burger` → `html.menu-open`, `lenis-stopped`, burger `aria-expanded=true` + aria-label "Close menu", mmenu `aria-hidden=false`, `visibility:visible`, `clip-path` `inset(0% 0% 100% 0%)` → `inset(0%)` over 0.8s `wipe`; links from yPercent 60/α0 0.9s stagger .06 @0.3; foot from y20/α0 0.8s @0.5. Escape (or a link click) reverses at timeScale 1.6 → `visibility:hidden`, `clip-path: inset(0% 0% 100%)`, `aria-hidden=true`.

## 5. Hero `section#top.hero` (relative, padding-top 76 / 64)
| | 1440 | 375 |
|---|---|---|
| section | `[0,0,1440,900]` | `[0,0,375,1233]` |
| `.wrap.hero__grid` | `[0,76,1440,736]`, grid `625.562px 579.25px`, gap 43.2px, padding 48.96px 96px 32px | `[0,64,375,970]`, grid `325px`, gap 24px, padding 36px 25px 20px |
| `.hero__copy` | flex column gap 30px `[96,153,626,599]` | `[25,100,325,596]` |
| `.hero__scene` | `[765,125,579,655]` (inline iso SVG `.iso-hero-scene` with about 80 CSS keyframes `iso*`; paused via `.is-paused` when hero is out of range) | `[25,720,325,294]` |
| `.hero__svg[data-parallax=-6]` | `[787,222,535,461]` | `[37,732,301,270]` |
| `.hero__guides` | flex, full section, vertical `<i>` guide lines | same |
| `.hero__foot` | grid `290.891px x4 + 84.406px` `[96,812,1248,88]`; `.fact` flex column gap 6 | grid `162.5px 162.5px` `[25,1034,325,199]` |
| `.hero__ctas` | flex gap 12 `[96,646,626,56]`; primary `[96,646,265,56]`, ghost "Watch the customer story" `[373,646,284,56]` | stacked: `[25,502,325,56]`, `[25,570,325,56]` |

Typography: eyebrow `.hero__eyebrow` Geist Mono 12px/18.6px ls 1.44px uppercase `#3D5A2A` ("Claims automation · ECHS & RGHS", `.sep` "/" `#CFC4AB`, `.hero__status` `#464B3A`); **h1** Perfectly Nineties **90.72px/88.9056px** ls -1.63296px `#1E2318` `[96,202,626,267]` (375: **46px/45.08px**, ls -0.828px, `[25,149,325,135]`), text "Scan the file. We’ll handle the claim."; `p.lede.hero__sub` 19.008px/29.4624px `#464B3A` (375: 17px/26.35px); `p.micro` 13px "Bring a real claim file…"; `.fact__k` Geist Mono 10px/15.5px ls 1.4px uppercase `#8A8C78`; `.fact__v` Geist 15px/23.25px; `a.scrollcue` Geist Mono 10px ls 1.4px `[1260,813,84,87]` (keyframes `cue`).
Scroll: `.hero__copy` to yPercent -14 / autoAlpha .25 (scrub, hero `top top`→`bottom top` = 0→900; 375: 0→1233). `.hero__svg` yPercent 0→-6 over the same range.

## 6. Proof `section.proof`
1440 `[0,900,1440,187]`: `.proof__in` grid `480px 768px`; `blockquote.proof__quote[data-reveal=fade]` flex column gap 14 `[96,924,480,186]`, quote `p[data-words]` Perfectly Nineties 27.36px/33.3792px; `.proof__logos` flex column gap 18 `[576,924,768,186]`; `.proof__label` Geist Mono 11px ls 1.32px uppercase `#6A6E5B` "Trusted by hospital claim desks"; `.logos` flex gap 12 with `.logo-lockup` (inline SVG/text, no image requests).
375 `[0,1233,375,392]`: single column; quote p 22px/26.84px.
Motion: quote words (SplitText words) start at opacity .08, on `top 88%` → anime `opacity .08→1, translateY .35em→0, blur(6px)→0`, 900ms, stagger 55ms, outExpo.

## 7. Problem `section#problem.problem` (padding 144 / 96)
1440 `[0,1087,1440,1000]`: `.problem__top` grid `315.094px 875.312px` gap 57.6px; `p.problem__statement[data-scrub-words]` Perfectly Nineties 50.4px/56.448px ls -0.4032px `[469,1231,875,226]`; `.costs[data-costs]` grid 4x`311.5px` `[96,1543,1248,362]`; `article.cost` flex column gap 40, padding 34px 30px, h 360; `.cost__k` Geist Mono 12px ls 1.44px `#6A6E5B`; `.cost__v` Perfectly Nineties 67.68px/64.296px ls -0.6768px; `.cost__unit` 31.1328px; `.cost__d` Geist 16px/24.8px `#464B3A`; `p.costs__note` 13px/19.5px `#6A6E5B`.
375 `[0,1625,375,1575]`: statement 30px/33.6px ls -0.24px; costs 1 column (323px), card h about 251, gap 28; `.cost__v` 48px/45.6px.
Motion: statement words opacity .13→1 (stagger .1, scrub true, `top 80%`→`bottom 48%`; desktop 511→1025, mobile 1114→1575). Cost cards start opacity 0 / translateY 70; on `.costs top 82%` anime 1300ms stagger 120 outExpo; each `[data-scramble-v]` value scrambles (chars `0123456789#%₹X`, speed .45, 1.1s, delay .35+i*.14). Hover `.cost:hover::before` scaleX 0→1 (olive 2px top bar, `transform .7s cubic-bezier(.7,0,.2,1)`, origin left).

## 8. Results `section#results.results[data-theme=dark]` (bg `#1B2414`, color `#F1ECDF`)
1440 `[0,2087,1440,801]`: `.sec-head` grid `675.562px 500.438px` gap 72; aside `span.mono` "MEASURED AT MEDIPULSE · ECHS & RGHS" Geist Mono 12px ls 1.2px `rgb(185,189,165)`; `.metrics` grid 3x416px `[96,2408,1248,262]`; `.metric[data-reveal=up]` flex column gap 22, padding 48px 48px 0 0; `.metric__k` Geist Mono 11px ls 1.32px uppercase `rgb(124,135,102)`; `.metric__v` Perfectly Nineties **112.32px**/95.472px ls -2.2464px (375: 72px/61.2px); `.metric__d` Geist 17px/25.5px `#C9CBB6`; `.results__bgnum[data-parallax=12]` "48%" Perfectly Nineties 489.6px, color `rgba(197,214,154,0.04)`; `p.results__note` Geist Mono 11px ls .66px.
375 `[0,3200,375,1254]`: 1 column, metric h 250.
Motion: section `clip-path inset(6% 3% 0% 3% round 28px)` → `inset(0% round 0px)` scrub `top bottom`→`top 25%` (1440: 1187→1862; 375: 2388→2997). Odometers `span.odo[data-odo]`: "3" with `data-from=7` (column 7,6,5,4,3; 1.6s), "66" and "48" spin (column i spins i+1 times through 0-9 then lands; 2.2s+0.25s*i), power4.inOut, delay .15, on `top 85%`. aria-labels are "7 days down to 3 days", "66 percent", "48 percent". `.metric__arrow .draw` DrawSVG 0→100%, .9s stagger .25 on `.metrics top 85%`. bgnum yPercent -12→12 scrub across section.

## 9. Movement (pinned) `section#movement.move` (bg `#F5F0E6`)
| | 1440 | 375 |
|---|---|---|
| section incl. pin spacer | `[0,2888,1440,5580]` | `[0,4454,375,5034]` |
| **Pin** | `pin: '.move__pin'`, start `top top` = **2888**, end `+= innerHeight*5.2` = **7568** (4680px), scrub **0.9**, anticipatePin 1, invalidateOnRefresh | **4454 → 8676** (4222px) |
| `.move__grid` | grid `482.156px 693.844px` gap 72 `[0,3015,1440,721]` | grid `325px` gap 14 |
| `.move__left` | flex column gap 26 | — |
| `ol.steps` | 6 `li.step` grid `36px 375.156px 33px` gap 8, h 51, padding 12px 0 12px 22px, `transition: color .4s` | grid 6 columns about 49px, gap 6, h 33 |
| `.stage` | `[650,3082,694,588]`: `.stage__hud` h 44 (Geist Mono 10px ls 1.2px uppercase), `.stage__canvas` `[651,3127,692,498]` (art scaled by `--art-s = min(w/600,h/420)*0.96`), `.stage__foot` h 44 Geist Mono 10.5px | hud `[26,4708,323,44]` |

Step text: `.step__n` Geist Mono 11px ls .88px `#3D5A2A`; `.step__t` Geist 17px/26.35px 500; `.step__time` Geist Mono 11px.
Scrubbed timeline TOTAL 7.0s; step starts `[0,1.1,2.2,3.3,4.4,5.6]`, names Watch/Read/Validate/Organise/Digistamp/Submit, clocks 00:03/07/11/14/19/26. Measured at 1440: y3600 → "Step 01 / 06 · Watch", y4500 → 02 Read, y5400 → 04 Organise, y6300 → 05 Digistamp, y7200 → 06 Submit; `.move__pin` is `position:fixed; top:0` throughout. Step change: `li.is-active`/`.is-done`, desc cross-fade (out y∓14 .35s power2.in; in .6s expo.out delay .18), log line fade .2→1. Steps are `role=button tabindex=0`; click/Enter scrolls to `start + (end-start)*((starts[i]+0.9)/7)` over 1.2s.

## 10. Product demo `section#product.demo` (bg `#EFE8D8`)
1440 `[0,8468,1440,1225]`: centered `.demo__head` flex column gap 22 `[330,8612,780,187]`; `.demo__stage` `[96,8856,1248,692]`; `.scaler[data-scale-w=1080]` scales `#pd.pd` (fixed-artboard, `transform: scale(min(1, w/1080))`); `p.demo__hint` 13px.
375 `[0,9488,375,740]`: artboard scaled to about 298 wide.
Motion: `.demo__tilt` `rotateX 24, scale .88, y 60` → 0/1/0 scrub `.demo__stage top 98%`→`top 30%` (1440 7974→8586; 375 9078→9630). `#pd` class cycles `pd pd-s0…pd-s6` every **3600ms** while active (`top 75%`→`bottom top`); 7 `button.pd-tl[data-go]` (01 Upload, 02 Prepare, 03 Audit, 04 Review, 05 Finalize, 06 Extract, 07 File on portal) jump and restart the timer. Hover `.pd-tl:hover .pd-tlt{color:#1E2318}`. Keyframes `pdIn pdOut pdSpin pdFill pdType`.

## 11. Platform `section#platform.platform`
1440 `[0,9692,1440,1123]`: sec-head grid `675.562px 500.438px`; h2 has `span.dim` "No re-work." `#8A8C78`; aside ghost btn--sm "See it on your claims"; `.pf[data-reveal=up]` grid `420px 826px` `[96,10141,1248,600]`; `button.pf__tab[data-tab]` flex column gap 10, padding 28px 32px, active bg `rgb(243,246,236)`, `transition: background-color .5s`; `.pf__num` Geist Mono 11px ls 1.32px; `.pf__title` Perfectly Nineties 28.8px/31.68px (375: 24px/26.4px); 3 `.pf__panel` with `img loading=lazy` validate.webp, stamp.webp, watcher.webp (1168x880 each) inside `.scaler[data-scale-w=828][data-fit=contain]`.
375 `[0,10228,375,1313]`: tabs stacked above `.pf__view` `[26,11280,323,234]`.
Behaviour (measured): tab 0 is active on load and `.pf__bar i` scaleY fills 0→1 over **7s** linear (only while `.pf` is between `top 70%` and `bottom 20%`, paused on hover), then auto-advances. Click tab 2 → `aria-selected` `[false,false,true]`, its bar scaleY 1, autoplay stops for good, the new panel gets `is-active` and wipes `clip-path inset(0 0 0 100%)`→`inset(0)` 1s expo.inOut, inner from x60/α0 1.2s delay .3, old inner x -40. Arrow keys move between tabs.

## 12. Trust `section#trust.trust`
1440 `[0,10815,1440,1007]`: `.trust__in` grid `550.234px 611.375px` gap 86.4; `.trust__frame[data-clip]` holds the `video` (trust-anim.mp4, 720x720, poster trust.webp, attrs `autoplay muted loop playsinline preload=metadata data-parallax-inner`); `figcaption.trust__cap` Geist Mono 10px ls 1.2px uppercase `#8A8C78` "Plate II · Measure, then file"; `.trust__copy` flex column gap 26; `.guarantees[data-guarantees]` grid 2x305.688px; `.g` flex column gap 8, padding 24px 28px 24px 0; `.g__t` Geist 16px/24.8px 600; `.g__d` Geist 15px/22.5px `#464B3A`.
375 `[0,11541,375,1424]`: 1 column, guarantees 1 column.
Motion: frame `clip-path inset(16%)` → `inset(0%)` scrub `top 95%`→`top 30%`; video `scale 1.35→1` scrub `top bottom`→`bottom top`; the video plays only while the frame is in range (`vid.muted=true` is set in JS, then play/pause on toggle). It is paused at page top and paused again once scrolled past. `.guarantees__rule` scaleX 0→1 1.4s expo.inOut; `.g` items opacity 0/y30 → 1/0, 1100ms, stagger 110 start 250, on `top 85%`.

## 13. Reconciliation `section#reconciliation.recon` (bg `#EFE8D8`)
1440 `[0,11822,1440,1368]`: `.sec-head--stack` (single column); `.recon__board[data-recon]` grid `320px 72px 856px` `[96,12275,1248,545]`; `.rsrc[data-recon-src]` x3 (`.rsrc__k` Geist Mono 10px ls 1.2px uppercase olive; `.rsrc__t` 16px 600; `.rsrc__d` 14px/21px); `.recon__wires path` (keyframes `wireflow`); dashboard `.rkpi__v` Perfectly Nineties 34px (375: 26px), `[data-count]` 48.2 / 44.9 / 39.6 / 5.3 (rendered as ₹48.2L etc.); `.rrow__id`/`.rrow__utr` Geist Mono 12px; `.rchip` Geist 12px 500 olive; `.rdash__note` Geist Mono 10px; `.recon__gains[data-stagger]` 3 x `.rgain` (h3 Perfectly Nineties 28.8px/33.12px, 375 24px/27.6px).
375 `[0,12965,375,2725]`.
Motion (on `.recon__board top 78%`, expo.out timeline): sources x-36/α0 → 0, 1.1s stagger .12 @0; wires α 0→1 .8s stagger .1 @.45; dash y50/α0 → 1.3s @.55; rows y14/α0 .8s stagger .09 @1.0; chips scale .6/α0 → 1, .6s stagger .09 back.out(2.2) @1.25; counters 0→value (toFixed(1)) 1.6s power3.out @.8; `.rrow--flag` bg `#FDF3EC`↔`#F9DCCB` .5s x4 yoyo @2.1. Gains stagger: 50px/α0 → 1200ms stagger 120.

## 14. Story `section#story.story[data-theme=dark]` (bg `#1B2414`)
1440 `[0,13190,1440,1162]`: `.story__frame[data-reveal=up]` → `.story__video[data-story]` 1226x690 holding `video` (testimonial.mp4 1280x720, poster poster.jpg, `preload=metadata playsinline`, **not** autoplay/muted/loop); `button.story__play` 128x128 circle bg `#C5D69A` color `#1B2414`, label "PLAY STORY" Geist Mono 10px ls 1.4px (375: 88x88); `.story__cap` p Perfectly Nineties 34.56px/39.744px (375: 18px/20.7px); `.story__bar i` progress (hover grows to 6px).
375 `[0,15690,375,587]`, video box 303x170.
Behaviour: the play button sits at the box center (`translate(613px,345px)` at 1440), starts `scale(0)` `visibility:hidden` and pops in (`scale 0→1` 1s back.out(1.8)) at `.story__video top 70%`. On fine pointers it follows the cursor (anime `createAnimatable`, 700ms, out(4)) and recenters on leave. Click anywhere toggles play. Labels: PAUSE / RESUME / REPLAY; section classes `is-playing has-started`; ArrowLeft/Right seek ±5s; bar click seeks.

## 15. Case `section#case.case`
1440 `[0,14352,1440,882]`: h2 `[96,14536,961,138]`; `.case__grid[data-stagger]` grid 3x415.33px `[96,14731,1248,359]`; `.case__col` flex column gap 16, padding 37.44px; `.case__col--dark` (night bg) with `.case__row` flex rows and `a.link` "Watch Mayank tell it →" `#C5D69A`; body p Geist 16px/25.92px `rgb(51,56,41)`.
375 `[0,16277,375,1180]`: 1 column, cols 323 wide.
Motion: children opacity 0/y50 → anime 1200ms stagger 120 outExpo on `top 85%`.

## 16. FAQ `section#faq.faq`
1440 `[0,15234,1440,974]`: `.faq__in` grid `464.641px 696.969px` gap 86.4; `.faq__left` flex column gap 24 with `p.body` + `a.link` info@dualite.dev; 7 `.qa`; `button.qa__q` grid `44px 608.969px 28px` gap 8, padding 26px 0, Perfectly Nineties 24.48px/29.376px (375: grid `32px 249px 28px`, 20px/24px); number `span.mono` Geist Mono 11px ls 1.1px `#8A8C78`; `.qa__icon` 28x28 (open: bg `#3D5A2A`, border 1px `#3D5A2A`; vertical bar `::after` is rotated 90deg when closed and flat when open; `transition: background-color .4s, border-color .4s`; hover border olive).
375 `[0,17457,375,1254]`.
Behaviour (measured): Q1 open on load (`aria-expanded=true`, `.qa__a` h **107** at 1440 / **156** at 375). Click Q2 → opens to 107 / 182 (height auto, .7s expo.out; inner y14/α0 → .7s delay .08). **Q1 stays open**: items toggle independently, this is not an exclusive accordion. Click again → 0 (.5s expo.inOut). `ScrollTrigger.refresh()` runs after each toggle.
Questions: 01 Which schemes and claim types do you support? · 02 Does Dualite submit claims without our approval? · 03 Do we need to change how we scan? · 04 What happens when a document is missing or doesn’t match? · 05 Where is our patient data stored? · 06 How do we know a claim has actually been paid? · 07 How long does it take to go live?

## 17. CTA / form `section#demo.cta[data-theme=dark]` (bg `#1B2414`)
1440 `[0,16208,1440,760]`: `.cta__in` grid 2x580.8px gap 86.4; h2 (no `.h2` class) Perfectly Nineties **72px/72px** ls -0.864px (375: 44px/44px ls -.528px); lede `#C9CBB6`; `ol.cta__list[data-stagger]` li Geist 15px/23.25px; `form#demo-form.form[data-reveal=up]` flex column gap 18 `[763,16428,581,459]`, card bg; `.form__grid` grid 2x242.4px gap 16; `label.field` Geist 13px 500; inputs/select h 50, bg `#FFFDF8`, border 1px `#CFC4AB`, padding 0 14px, Geist 15px 500, `transition: border-color .3s, box-shadow .3s`; honeypot `label` "Website" positioned offscreen (x about -9236); submit `button.btn.btn--primary` full width h 56 "Book my demo"; `.form__note` 13px; `.form__done` overlay (h3 "Thank you." Perfectly Nineties 34px).
375 `[0,18711,375,1513]`: 1 column, form grid 277px.
Behaviour: required/invalid fields get border `#B04A1E` + `aria-invalid` + shake `translateX [0,-8,7,-5,3,0]` 520ms. A valid submit POSTs JSON to **`/api/lead`** (15s abort); success shows the done overlay (clip wipe .9s + seal draw); failure shows a mailto fallback in `.form__error`. Not exercised live, because submitting would create a real lead.

## 18. Footer `footer.footer[data-theme=dark]` (bg `#131A0E`, color `rgb(185,189,165)`)
1440 `[0,16967,1440,658]`: `.footer__in` padding 86.4px 96px 0; `.footer__top` grid `706.562px 493.438px` gap 48 (logo-light.png 100x24 + `p.footer__tag` Perfectly Nineties 28.8px/36px `rgb(217,219,200)`); `.footer__cols` flex gap 72: PRODUCT / GUIDES (`/blog/rghs-claim-submission-guide/`, `/blog/echs-claim-submission-guide/`, `/blog/cghs-claim-submission-guide/`, `/blog/`) / COMPANY; headings `span.mono` Geist Mono 11px ls 1.32px `#C5D69A`; links 15px `rgb(217,219,200)`; `.footer__mark[data-footer-mark]` "Scan <em>&</em> forget." giant display; `.footer__bar` flex gap 16 h 68 ("© 2026 DUALITE", "PRIVACY · TERMS", `button[data-top]` "BACK TO TOP ↑" Geist Mono 11px ls .88px → lenis scrollTo 0 over 2s).
375 `[0,20224,375,804]`, padding 64px 25px 0; top 1 column, cols flex gap 40.
Motion: mark chars (SplitText chars, masked) from yPercent 110, 1.4s stagger .04 expo.out on `top 95%`; `.footer__top` from y60/α0 1.4s on `.footer top 85%`.

---

## 19. Motion inventory: generic systems
- **Lenis 1.3.26**: `new Lenis({duration:1.15, easing:t=>Math.min(1,1.001-2**(-10*t)), smoothWheel:true})`, bridged to `gsap.ticker` (`lenis.raf(t*1000)`, `lagSmoothing(0)`), `lenis.on('scroll', ScrollTrigger.update)`. html gets `lenis` (plus `lenis-stopped` during loader/menu). Disabled under reduced motion. `history.scrollRestoration='manual'`; `ScrollTrigger.config({ignoreMobileResize:true})`.
- **Eyebrows `[data-scramble]`** (11): text node moved into `span.eyebrow__txt`, emptied; on `top 90%` ScrambleText (A-Z0-9, 1.1s, speed .5, revealDelay .15) and `.eyebrow__idx` blinks autoAlpha .3s x3 yoyo.
- **Headings `[data-split]`** (10 h2): SplitText lines with mask, `autoSplit`; from yPercent 112, rotate 2.5, origin 0 0, 1.35s, stagger .1, expo.out, `top 88%` once.
- **`[data-reveal]`** (18): `fade` = from autoAlpha 0, y 24, 1.2s; `up` = y 70, 1.5s; plus `blur(8px)` when innerWidth>980; expo.out; `top 90%` once; filter cleared after. Measured start state at 375: `.metric` opacity 0, visibility hidden, `matrix(1,0,0,1,0,70)`; `.results__note` `translateY(24px)`.
- **`[data-stagger]`** (recon__gains, case__grid, cta__list): kids opacity 0/y50 → anime 1200ms stagger 120 outExpo at `top 85%`.
- **`[data-parallax]`**: `.hero__svg` (-6, `top top`→`bottom top`), `.results__bgnum` (12, from -12, `top bottom`→`bottom top`).
- **Hover states (CSS + measured)**:
  - `.roll` (overflow hidden) > span carries `text-shadow: 0 <line-height> 0 currentColor` (18.75px nav, 20px buttons); `.nav__links a:hover .roll>span`, `.btn:hover .roll>span` → `translateY(-100%)` (measured nav `matrix(...,-18.75)`, button `-20`), `transition: transform .6s cubic-bezier(.7,0,.2,1)`.
  - `.btn::before` (inset -1px; primary bg `#1B2414`, ghost bg `#1E2318`) rests at `translateY(100%+)` (measured 44.44 / 56.56) and goes to `none` on hover/focus-visible, .6s ease-io. Ghost hover: color `#F5F0E6`, border `#1E2318` (in dark sections color `#1B2414`). `.btn` transition `color .5s, border-color .5s` ease-io.
  - `.btn__icon` has two arrow svgs: on hover the first goes `translateX(140%)` (measured 22.4px) and the second comes to `none`.
  - **Magnetic `[data-magnetic]`** (5 elements; fine pointer only, so disabled at 375 touch): `gsap.quickTo` x = (dx·0.22), y = (dy·0.30), .6s power3.out; measured `translate(28.0156px, 6.8719px)` with the cursor at the bottom-right corner (-5,-5) of the 265x56 hero button; on leave → 0,0 with `elastic.out(1,0.45)` .9s.
  - `.link:hover` background-size `0 1px` ↔ `100% 1px` .5s ease-io (`.link--on:hover` runs keyframes `relink .8s`).
  - `.cost:hover::before` scaleX 1; `.qa__q:hover .qa__icon` border olive; `.pd-tl:hover .pd-tlt` ink.

### ScrollTrigger table, 1440x900 (start → end in scroll px)
```
hero: 0→900 (3x: copy scrub, svg parallax scrub, scene pause toggle)
proof__quote / proof__logos reveal 114 (once) · proof p[data-words] 176 (once)
problem eyebrow 421 · problem__statement scrub 511→1025 · costs 805 · costs__note 1137
results clip scrub 1187→1862 · bgnum parallax 1187→2888 · eyebrow 1421 · h2 1479 · aside 1532
metrics arrow 1643 · metric x3 1669 · odo x3 1790 · results__note 1941
movement PIN .move__pin 2888→7568 scrub 0.9
move eyebrow 2205 · move h2 2268 · demo eyebrow 7802 · demo h2 7860 · demo lede 7954
demo__tilt scrub 7974→8586 · #pd autoplay toggle 8241→9525
platform eyebrow 9026 · h2 9085 · aside 9085 · .pf reveal 9331 · .pf autoplay toggle 9511→10561
trust eyebrow 10149 · h2 10212 · frame clip scrub 10175→10760 · video scale scrub 10130→11580 · video play toggle 10130→11580 · lede 10382 · guarantees 10526
recon eyebrow 11157 · h2 11216 · aside 11313 · board 11573 · gains 12112
story eyebrow 12524 · h2 12583 · who 12603 · frame 12756 · play btn 12947
case eyebrow 13686 · h2 13744 · grid 13966
faq eyebrow 14569 · h2 14629 · body 14798
cta eyebrow 15542 · h2 15604 · form 15618 · lede 15789 · list 15901
footer top 16202 · footer mark 16493
nav state 0→16726 · progress scrub(0.3) 0→16726
is-dark toggles: results 2049→2850, story 13152→14314, cta 16170→16929, footer 16929→17588
aria-current: results 1682→2483, movement 2483→8063, platform 9287→10410, trust 10410→11417, faq 14829→15803
```
### Non-once triggers, 375x812
```
hero 0→1233 · problem__statement 1114→1575 · results clip 2388→2997 · bgnum 2388→4454
movement PIN 4454→8676 (scrub 0.9) · demo__tilt 9078→9630 · #pd 9325→10100 · .pf 10184→11353
trust clip 10866→11394 · trust video 10825→11962 · nav/progress 0→20216
is-dark: results 3162→4416, story 15652→16239, cta 18673→20186, footer 20186→20990
aria-current: results 2835→4088, movement 4088→9122, platform 9863→11176, trust 11176→12599, faq 17092→18346
```

---

## 20. Asset inventory (every request the original makes, full-page scroll at both widths)
| URL | Type | Bytes | When | In clone `public/`? |
|---|---|---|---|---|
| `/` | html | 42955 | load | n/a (Vite index.html) |
| `/pn-regular.woff2`, `/pn-italic.woff2` | font (preload, crossorigin) | 18900 / 20428 | load | yes (byte-identical) |
| `fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap` | css | — | load | replaced by `/fonts.css` |
| `fonts.gstatic.com/s/geist/v5/gyByhwUxId8gMEwcGFWNOITd.woff2`, `…gyByhwUxId8gMEwSGFWNOITddY4.woff2` | font (variable, latin + latin-ext) | 29288 / 16540 | load | different files: clone uses older static `gyBhhwUx…` per-weight files (400/500/600). Renders identically in the measured roles |
| `fonts.gstatic.com/s/geistmono/v6/or3nQ6H-…FrcdmhHkjko.woff2`, `…FrkdmhHkjkotbA.woff2` | font | 23108 / 14712 | load | same note (`or3yQ6H…` 400/500) |
| `/assets/css/site.css`, `hero-scene.css`, `demo.css` | css | 56388 / 31052 / 7450 | load | yes (identical size + ETag-matched size) |
| `/logo-dark.png`, `/logo-light.png` | png 386x64 | 9287 / 11923 | load | yes |
| `/trust.webp` (video poster) | webp | 256886 | load | yes |
| `/poster.jpg` (story poster, og:image) | jpeg | 25166 | load | yes |
| gsap 3.15.0 core, ScrollTrigger, SplitText, ScrambleTextPlugin, DrawSVGPlugin, CustomEase · animejs 4.5.0 UMD · lenis 1.3.26 (jsdelivr) | js | 72927 / 44575 / 7732 / 11687 / 4351 / 7143 / 118043 / 18722 decoded | load | yes, `public/vendor/*` byte-identical |
| `/assets/js/site.js` | js | 49805 | load | yes |
| `/trust-anim.mp4` | mp4 720x720, 206 ranges | 313864 | load (metadata), refetched when the frame enters view | yes |
| `/testimonial.mp4` | mp4 1280x720, 206 | 10218115 | metadata at load | yes |
| `/validate.webp`, `/stamp.webp`, `/watcher.webp` | webp 1168x880, `loading=lazy` | 319238 / 266654 / 319604 | **lazy, only when scrolling near #platform** | yes |
| favicon | inline `data:image/svg+xml` | — | — | in index.html |

No CSS `url()` assets beyond the two Perfectly Nineties fonts (all other backgrounds are data-URIs/gradients). No IntersectionObserver usage in the site code; every scroll-linked behaviour is ScrollTrigger (plus a `ResizeObserver` on `.scaler, .stage__canvas` that refits scalers).

Linked but outside this single-page clone: `/blog/` (live returns 200 with a real blog; the clone's Vite server answers 200 with the SPA homepage HTML, so it is a soft 404) plus the three `/blog/*-claim-submission-guide/` links in the footer; `POST /api/lead` (form backend, not present under Vite, so a valid submit falls into the mailto-fallback error state); `mailto:info@dualite.dev`.
