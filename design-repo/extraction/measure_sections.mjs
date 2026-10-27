// Optional re-measure tool for R9 section heights (not run by verify_all.py).
//
//   PLAYWRIGHT_MODULE=<path-to-playwright-package> node extraction/measure_sections.mjs <url> [out.json]
//
// PLAYWRIGHT_MODULE defaults to the bare specifier "playwright". Measures every section box at
// 1440x900 (DPR 1) after the intro has finished (sessionStorage dc-intro=1 is preset so the
// once-per-session loader does not block), keyed by the semantic section ids used in
// templates/templates.json. Paste the result into extraction/measured-values.json ->
// sectionHeights.pages["/"].live (or .clone) and re-run extraction/verify_all.py.
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const [url, out] = process.argv.slice(2);
if (!url) { console.error('usage: measure_sections.mjs <url> [out.json]'); process.exit(2); }
const MAP = {
  '.skip': 'utility.skip-link', '.loader': 'runtime.intro-loader', '.progress': 'utility.scroll-progress', '.grain': 'utility.grain-overlay',
  '#nav': 'shell.navbar', '#mmenu': 'runtime.mobile-menu', '.hero': 'hero.claims-intro', '.proof': 'proof.quote-logos', '.problem': 'content.problem-costs',
  '.results': 'metrics.results-band', '.move': 'features.pinned-workflow', '.demo': 'product.demo-walkthrough', '.platform': 'features.platform-tabs',
  '.trust': 'trust.guarantees', '.recon': 'features.reconciliation', '.story': 'proof.video-story', '.case': 'editorial.case-study', '.faq': 'faq.accordion',
  '.cta': 'conversion.demo-form', '.footer': 'shell.footer',
};
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await ctx.addInitScript(() => { try { sessionStorage.setItem('dc-intro', '1'); } catch (e) {} });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'load', timeout: 90000 });
await page.waitForTimeout(3000);
const res = await page.evaluate((map) => {
  const o = { docHeight: document.documentElement.scrollHeight, sections: {} };
  for (const [sel, id] of Object.entries(map)) {
    const e = document.querySelector(sel); if (!e) continue;
    const r = e.getBoundingClientRect(), pos = getComputedStyle(e).position;
    o.sections[id] = { selector: sel, top: Math.round(r.top + scrollY), height: Math.round(r.height), position: pos, inFlow: pos !== 'fixed' && pos !== 'sticky' };
  }
  return o;
}, MAP);
await browser.close();
const json = JSON.stringify({ viewport: { width: 1440, height: 900, deviceScaleFactor: 1 }, url, measuredAt: new Date().toISOString(), ...res }, null, 1);
if (out) fs.writeFileSync(out, json); else console.log(json);
