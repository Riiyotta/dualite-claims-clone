// Live-vs-clone pixel parity harness (R12). Optional tool; not run by verify_all.py.
//
//   PLAYWRIGHT_MODULE=<path-to-playwright-package> \
//   node extraction/parity_harness.mjs <liveUrl> <cloneUrl> <out.json>
//
// PLAYWRIGHT_MODULE defaults to the bare specifier "playwright" (resolved normally).
// Both pages are rendered under identical, deterministic conditions so the compare
// measures layout/paint parity rather than animation phase:
//   - viewport 1440x900, DPR 1, prefers-reduced-motion: reduce (the site's own
//     reduced-motion branch: no loader, no Lenis, reveals set to final state)
//   - sessionStorage dc-intro=1 (intro already seen this session)
//   - CSS animations/transitions disabled, grain overlay + fixed nav + progress hidden,
//     videos paused at t=0 (poster frame)
// For every in-flow section, viewport screenshots are taken at the section top and
// every further 900px (max 6 frames). Each frame pair is compared in a canvas: a
// pixel matches when every RGB channel differs by <= 16. The per-section score is the
// mean of its frames. Gate: every section >= 80% AND page mean >= 80%.
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const [live, clone, out] = process.argv.slice(2);
if (!live || !clone || !out) { console.error('usage: parity_harness.mjs <liveUrl> <cloneUrl> <out.json>'); process.exit(2); }
const SECTIONS = ['.hero', '.proof', '.problem', '.results', '.move', '.demo', '.platform', '.trust', '.recon', '.story', '.case', '.faq', '.cta', '.footer'];
const CSS = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}.grain,#nav,.progress{visibility:hidden!important}';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function capture(browser, url) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, reducedMotion: 'reduce' });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('dc-intro', '1'); } catch (e) {} });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load', timeout: 90000 });
  await page.addStyleTag({ content: CSS });
  await sleep(2500);
  await page.evaluate(() => document.querySelectorAll('video').forEach((v) => { try { v.pause(); v.currentTime = 0; } catch (e) {} }));
  const res = {};
  for (const sel of SECTIONS) {
    const box = await page.evaluate((s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return { y: Math.round(r.top + scrollY), h: Math.round(r.height) }; }, sel);
    if (!box) { res[sel] = null; continue; }
    const frames = [];
    for (let off = 0; off < box.h && frames.length < 6; off += 900) {
      await page.evaluate((y) => window.scrollTo(0, y), box.y + off);
      await sleep(700);
      await page.evaluate(() => document.querySelectorAll('video').forEach((v) => { try { v.pause(); } catch (e) {} }));
      const visH = Math.min(900, box.h - off);
      frames.push((await page.screenshot({ clip: { x: 0, y: 0, width: 1440, height: visH } })).toString('base64'));
    }
    res[sel] = { box, frames };
  }
  await ctx.close();
  return res;
}

async function compare(browser, a, b) {
  const page = await browser.newPage();
  const score = await page.evaluate(async ([A, B]) => {
    const load = (s) => new Promise((r) => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
    const [ia, ib] = await Promise.all([load(A), load(B)]);
    const w = Math.min(ia.width, ib.width), h = Math.min(ia.height, ib.height);
    const px = (img) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(0, 0, w, h).data; };
    const da = px(ia), db = px(ib); let ok = 0;
    for (let i = 0; i < da.length; i += 4) if (Math.abs(da[i] - db[i]) <= 16 && Math.abs(da[i + 1] - db[i + 1]) <= 16 && Math.abs(da[i + 2] - db[i + 2]) <= 16) ok++;
    return ok / (w * h);
  }, [a, b]);
  await page.close();
  return score;
}

const browser = await chromium.launch();
const L = await capture(browser, live), C = await capture(browser, clone);
const sections = {};
for (const sel of SECTIONS) {
  if (!L[sel] || !C[sel]) { sections[sel] = { error: 'missing on one side' }; continue; }
  const n = Math.min(L[sel].frames.length, C[sel].frames.length), s = [];
  for (let i = 0; i < n; i++) s.push(await compare(browser, L[sel].frames[i], C[sel].frames[i]));
  sections[sel] = { liveBox: L[sel].box, cloneBox: C[sel].box, frames: n, perFrame: s.map((v) => +(v * 100).toFixed(2)), matchPct: +((s.reduce((x, y) => x + y, 0) / n) * 100).toFixed(2) };
}
// Negative control: two different sections must NOT match (proves the compare discriminates).
const negativeControlPct = +((await compare(browser, L['.hero'].frames[0], C['.results'].frames[0])) * 100).toFixed(2);
if (process.env.PARITY_SAVE_DIR) for (const s of ['.hero', '.recon']) { fs.writeFileSync(`${process.env.PARITY_SAVE_DIR}/live${s.replace('.', '_')}.png`, Buffer.from(L[s].frames[0], 'base64')); fs.writeFileSync(`${process.env.PARITY_SAVE_DIR}/clone${s.replace('.', '_')}.png`, Buffer.from(C[s].frames[0], 'base64')); }
await browser.close();
const vals = Object.values(sections).filter((v) => typeof v.matchPct === 'number').map((v) => v.matchPct);
const result = {
  method: 'viewport 1440x900 DPR1, reducedMotion=reduce, dc-intro=1, animations/transitions off, grain/nav/progress hidden, videos paused; per-pixel RGB tolerance 16',
  live, clone, measuredAt: new Date().toISOString(), sections,
  averagePct: +(vals.reduce((x, y) => x + y, 0) / vals.length).toFixed(2),
  minSectionPct: Math.min(...vals),
  gate: { perSectionMin: 80, averageMin: 80 },
  negativeControl: { compare: 'live .hero frame 0 vs clone .results frame 0 (different sections)', matchPct: negativeControlPct, expect: 'well below 80' },
};
result.pass = result.minSectionPct >= 80 && result.averagePct >= 80;
fs.writeFileSync(out, JSON.stringify(result, null, 1));
console.log(JSON.stringify({ negativeControlPct, averagePct: result.averagePct, minSectionPct: result.minSectionPct, pass: result.pass, per: Object.fromEntries(Object.entries(sections).map(([k, v]) => [k, v.matchPct ?? v.error])) }, null, 1));
