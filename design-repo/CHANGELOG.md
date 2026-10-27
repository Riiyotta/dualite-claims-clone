# Changelog

## 1.0.0 (2026-10-27): initial build (Situation A)

- Built from scratch from the clone source (`src/components/*.jsx`, `public/assets/css/site.css`,
  `public/assets/js/site.js`, `index.html`) and the measured `CLONE_SPEC.md`. A sample of
  CLONE_SPEC claims was re-checked against source: section order, the :root tokens, loader markup,
  head gating script, pin config, and the `/api/lead` endpoint.
- Tokens: 23 foundation colours from :root, plus typography, spacing (gap histogram), radius,
  elevation, breakpoints and motion. Also semantic, component and layout tokens, light and dark
  themes, and the generated `tokens/llm/token-catalog.json` with `token-policy.json`.
- 20 section contracts, each with a closed `source` / `semantic` split, structured responsive
  fields, motion patterns with locked reduced-motion fallbacks, and `generatedAssetRoles`. Five are
  `retrievalEligible: false`: skip link, intro loader, scroll progress, grain overlay and mobile
  menu. The form submit feedback component is also ineligible.
- Intro loader specified as a first-class contract, with structure, tokens, the full anime.js
  timeline, measured offsets and gating. It has a generation-safe variant in the generated example.
- One template (`template.home`). The four blog routes are documented as not implemented by the
  clone (soft-404 SPA fallback).
- PageSpec schema 1.0.0 with a required `mode` (reference | generated), generated from the
  contracts. The semantic validator covers template cross-check, graph rules, maxWords, assetRole
  per slot, pins, token policy, and generated-mode leakage rules.
- Asset roles with three-way availability, pinned in code. Real logos, product screenshots, the
  testimonial video and poster, customer logos and the live endpoint are blocked for generation.
- Measured 1440 section heights plus the wrapper gate (no whitelist needed: hero 900px, largest
  section 31.7%). Live-vs-clone pixel parity was measured: every section >= 99.93%.
- Correction recorded: the loader seal is drawn by anime.js, not GSAP DrawSVG.
- Counts in the README and manifest are recomputed by `verify_all.py --write-counts`.
