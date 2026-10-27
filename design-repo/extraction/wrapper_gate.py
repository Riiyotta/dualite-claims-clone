#!/usr/bin/env python3
"""Whole-page-wrapper quality gate (R9). Called from extraction/verify_all.py; also runnable alone.

    python3 extraction/wrapper_gate.py [--mv <measured-values.json>] [--whitelist <wrapper-whitelist.json>]

Reads measured section heights (extraction/measured-values.json -> sectionHeights, measured at
1440px) and, for every template route, checks:
  - HERO > 1800px: warn; HERO > 3000px: error unless whitelisted
  - one in-flow section > 50% of the page: warn; > 60%: error unless whitelisted
    (pages with < 3 in-flow sections are skipped; SHELL/UTILITY/RUNTIME excluded;
     fixed/sticky elements take no page height)
  - missing measurement for a template node: error; wrong viewport: error
  - whitelist entries need reviewedBy, justification >= 30 chars, maxHeightPx above the
    measured height; agent reviewers must say "agent attestation, not a human sign-off";
    stale (not triggering) or over-cap entries fail. A whitelisted hit still warns.
Thresholds are pinned here, not read from JSON.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWPORT_WIDTH = 1440
HERO_WARN_PX, HERO_ERROR_PX = 1800, 3000
SHARE_WARN, SHARE_ERROR = 0.50, 0.60
MIN_INFLOW = 3
EXCLUDED_CATEGORIES = {"SHELL", "UTILITY", "RUNTIME"}
AGENT_PHRASE = "agent attestation, not a human sign-off"


def run(root=ROOT, mv_path=None, wl_path=None):
    root = Path(root)
    errors, warnings, info = [], [], []
    mv = json.loads(Path(mv_path or root / "extraction/measured-values.json").read_text())
    wl = json.loads(Path(wl_path or root / "extraction/wrapper-whitelist.json").read_text()).get("entries", [])
    sections = {json.loads(p.read_text())["id"]: json.loads(p.read_text()) for p in (root / "sections").glob("*.json")}
    templates = json.loads((root / "templates/templates.json").read_text())["templates"]
    sh = mv.get("sectionHeights")
    if not sh:
        return ["sectionHeights missing from measured-values.json"], warnings, info
    if sh.get("viewport", {}).get("width") != VIEWPORT_WIDTH:
        errors.append(f"sectionHeights measured at width {sh.get('viewport', {}).get('width')}, gate requires {VIEWPORT_WIDTH}")
    used = set()
    for tid, t in templates.items():
        for route in t["routes"]:
            page = sh.get("pages", {}).get(route)
            if not page:
                errors.append(f"{route}: no height measurement for template {tid}")
                continue
            for side in ("live", "clone"):
                m = page.get(side)
                if not m:
                    errors.append(f"{route}: missing {side} measurement")
                    continue
                meas = m["sections"]
                inflow = []
                for n in t["nodes"]:
                    sid = n["section"]
                    if sid not in meas:
                        errors.append(f"{route} [{side}]: missing measurement for {sid}")
                        continue
                    cat = sections[sid]["semantic"]["category"]
                    if cat in EXCLUDED_CATEGORIES or not meas[sid].get("inFlow", True):
                        continue
                    inflow.append((sid, cat, meas[sid]["height"]))
                total = sum(h for _, _, h in inflow)
                for sid, cat, h in inflow:
                    share = h / total if total else 0
                    hit = []
                    if cat == "HERO" and h > HERO_WARN_PX:
                        hit.append(("hero", h > HERO_ERROR_PX))
                    if len(inflow) >= MIN_INFLOW and share > SHARE_WARN:
                        hit.append(("share", share > SHARE_ERROR))
                    for kind, fatal in hit:
                        entry = next((e for e in wl if e.get("route") == route and e.get("section") == sid and e.get("kind") == kind), None)
                        msg = f"{route} [{side}] {sid} ({cat}) {h}px = {share:.1%} of in-flow page height {total}px"
                        if entry:
                            used.add((route, sid, kind))
                            problems = whitelist_problems(entry, h)
                            if problems:
                                errors.extend(f"whitelist {route}/{sid}/{kind}: {p}" for p in problems)
                            warnings.append(msg + f" [whitelisted by {entry.get('reviewedBy')}]")
                        elif fatal:
                            errors.append(msg + f" exceeds {'HERO 3000px' if kind == 'hero' else '60% share'} and is not whitelisted")
                        else:
                            warnings.append(msg + f" exceeds {'HERO 1800px' if kind == 'hero' else '50% share'} (warning)")
                if side == "live":
                    top = max(inflow, key=lambda x: x[2]) if inflow else None
                    if top:
                        info.append(f"{route}: {len(inflow)} in-flow sections, total {total}px; largest {top[0]} {top[2]}px = {top[2] / total:.1%}; hero {next((h for s, c, h in inflow if c == 'HERO'), 'n/a')}px")
    for e in wl:
        if (e.get("route"), e.get("section"), e.get("kind")) not in used:
            errors.append(f"stale whitelist entry {e.get('route')}/{e.get('section')}/{e.get('kind')}: it no longer triggers the gate")
    return errors, warnings, info


def whitelist_problems(e, h):
    p = []
    if not e.get("reviewedBy"):
        p.append("missing reviewedBy")
    elif "agent" in e["reviewedBy"].lower() and AGENT_PHRASE not in e["reviewedBy"].lower():
        p.append(f"agent reviewer must state '{AGENT_PHRASE}'")
    if len(e.get("justification", "")) < 30:
        p.append("justification shorter than 30 chars")
    if not isinstance(e.get("maxHeightPx"), (int, float)):
        p.append("missing maxHeightPx")
    elif e["maxHeightPx"] < h:
        p.append(f"measured {h}px exceeds maxHeightPx {e['maxHeightPx']}")
    return p


if __name__ == "__main__":
    a = sys.argv
    mv = a[a.index("--mv") + 1] if "--mv" in a else None
    wl = a[a.index("--whitelist") + 1] if "--whitelist" in a else None
    e, w, i = run(mv_path=mv, wl_path=wl)
    for x in i:
        print("INFO ", x)
    for x in w:
        print("WARN ", x)
    for x in e:
        print("ERROR", x)
    print(f"wrapper gate: {len(e)} error(s), {len(w)} warning(s)")
    sys.exit(1 if e else 0)
