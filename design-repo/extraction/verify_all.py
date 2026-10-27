#!/usr/bin/env python3
"""Single entry point that proves the design-repo is internally consistent and grounded.

    python3 extraction/verify_all.py [--source-root <clone project dir>] [--write-counts]

--source-root (or env DESIGN_REPO_SOURCE_ROOT) defaults to measured-values.json "sourceRoot"
("..", the clone project that contains this design-repo). When that tree is absent (a standalone
copy of the package) the citation re-reads degrade to WARN; everything else still runs.
--write-counts recomputes registry.manifest.json counts and the README counts block from disk.

Checks (each prints PASS/FAIL/WARN): json parse, closed section-contract schema, source/semantic
split + source re-read (tag/marker at the cited line), every evidence citation (range + expected
text), allowlist parity (ids, node properties, asset roles, motion patterns, version), schema
parity (regenerated from contracts), template/contract/route mapping, graph <-> validator rule
agreement, PINNED_AVAILABILITY (own copy == validator copy == registry), RETRIEVAL_INELIGIBLE pin,
motion pattern wiring, token catalog/policy parity (+ colour values vs source CSS), example
PageSpecs (schema + semantic, one generated example per template), wrapper gate, manifest
entryPoints/counts/README counts, hygiene (absolute paths, junk files).
"""
import json, os, re, sys, importlib.util
sys.dont_write_bytecode = True
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- pins (verify_all's OWN copies; must equal the validator's)
PINNED_AVAILABILITY = {
    "brand.logo-source": "blocked-for-generation",
    "mark.seal-source": "reference-only",
    "illustration.hero-scene-source": "reference-only",
    "illustration.workflow-stage-source": "reference-only",
    "screenshot.product-ui-source": "blocked-for-generation",
    "screenshot.platform-source": "blocked-for-generation",
    "video.trust-animation-source": "reference-only",
    "video.testimonial-source": "blocked-for-generation",
    "image.story-poster-source": "blocked-for-generation",
    "logo.customer-source": "blocked-for-generation",
    "endpoint.lead-source": "blocked-for-generation",
    "brand.mark-placeholder": "generation-safe",
    "mark.seal-generic": "generation-safe",
    "illustration.generated": "generation-safe",
    "image.generated-product-visual": "generation-safe",
    "video.generated-loop": "generation-safe",
    "video.user-supplied": "generation-safe",
    "image.generated-poster": "generation-safe",
    "logo.customer-placeholder": "generation-safe",
    "person.fictional": "generation-safe",
    "rating.placeholder": "generation-safe",
    "url.placeholder": "generation-safe",
    "endpoint.placeholder": "generation-safe",
    "copy.original": "generation-safe",
}
RETRIEVAL_INELIGIBLE = {"utility.skip-link", "runtime.intro-loader", "utility.scroll-progress", "utility.grain-overlay", "runtime.mobile-menu"}
RETRIEVAL_INELIGIBLE_COMPONENTS = {"component.form-feedback"}
RUNTIME_ID_PATTERN = re.compile(r"(loader|preload|skip|progress|grain|overlay|mobile-menu|drawer|modal|dialog|toast|cookie|consent|cursor|feedback)", re.I)
# Built from fragments so this file never contains the literal prefixes it searches for.
_U, _H, _P = "/" + "Users/", "/" + "home/", "/" + "private/"
ABS_PATH = re.compile(re.escape(_U) + r"[A-Za-z0-9._-]+/|" + re.escape(_H) + r"[A-Za-z0-9._-]+/|" + re.escape(_P) + r"(tmp|var)/|[A-Z]:\\\\?" + "Users")
JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}

results = []


def rec(status, name, detail=""):
    results.append((status, name, detail))


def load(rel):
    return json.loads((ROOT / rel).read_text())


def module(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def source_root():
    a = sys.argv
    if "--source-root" in a:
        return Path(a[a.index("--source-root") + 1]).resolve()
    if os.environ.get("DESIGN_REPO_SOURCE_ROOT"):
        return Path(os.environ["DESIGN_REPO_SOURCE_ROOT"]).resolve()
    return (ROOT / load("extraction/measured-values.json").get("sourceRoot", "..")).resolve()


def iter_evidence(obj, where):
    if isinstance(obj, dict):
        if set(obj) >= {"cite", "expect"} and isinstance(obj["cite"], str):
            yield where, obj
        for k, v in obj.items():
            yield from iter_evidence(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_evidence(v, f"{where}[{i}]")


def compute_counts():
    secs = list((ROOT / "sections").glob("*.json"))
    tpl = load("templates/templates.json")["templates"]
    routes = load("templates/routes.json")
    adv = module("schema/tests/adversarial_test.py", "adv_counts")
    return {
        "foundationTokens": sum(1 for t in load("tokens/llm/token-catalog.json")["tokens"].values() if "00-foundation" in t["source"]),
        "catalogTokens": load("tokens/llm/token-catalog.json")["count"],
        "primitives": len(list((ROOT / "primitives").glob("*.json"))),
        "components": len(list((ROOT / "components").glob("*.json"))),
        "sections": len(secs),
        "retrievalIneligibleSections": sum(1 for p in secs if json.loads(p.read_text()).get("retrievalEligible") is False),
        "templates": len(tpl),
        "routesImplemented": len(routes["routes"]),
        "routesNotImplementedByClone": len(routes["notImplementedByClone"]),
        "assetRoles": len(load("assets/asset-roles.json")["roles"]),
        "generationSafeAssetRoles": sum(1 for r in load("assets/asset-roles.json")["roles"].values() if r["availability"] == "generation-safe"),
        "motionPatterns": len(load("tokens/00-foundation/motion-patterns.json")["patterns"]),
        "graphRules": len(load("compatibility/graph.json")["rules"]),
        "examplePageSpecs": len(list((ROOT / "schema/examples").glob("*.pagespec.json"))),
        "adversarialMutations": len(adv.MUTATIONS),
        "adversarialControls": len(adv.CONTROLS),
    }


def readme_block(counts):
    lines = ["<!-- COUNTS:BEGIN (generated by extraction/verify_all.py --write-counts; do not hand-edit) -->", "| Item | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in counts.items()]
    lines.append("<!-- COUNTS:END -->")
    return "\n".join(lines)


def main():
    try:
        checks()
    except Exception as e:  # a crash is a failure, never a silent pass
        import traceback
        rec("FAIL", "verify_all crashed", f"{type(e).__name__}: {e} @ {traceback.extract_tb(e.__traceback__)[-1].lineno}")
    for s, n, d in results:
        print(f"{s:4}  {n:46} {d}")
    f = sum(1 for s, _, _ in results if s == "FAIL")
    print(f"\nverify_all: {sum(1 for s, _, _ in results if s == 'PASS')} pass, {f} fail, {sum(1 for s, _, _ in results if s == 'WARN')} warn")
    return 1 if f else 0


def checks():
    # 0. JSON parse
    bad = []
    for p in ROOT.rglob("*.json"):
        try:
            json.loads(p.read_text())
        except Exception as e:
            bad.append(f"{p.relative_to(ROOT)}: {e}")
    rec("FAIL" if bad else "PASS", "json parse", "; ".join(bad[:3]) or f"{len(list(ROOT.rglob('*.json')))} files")

    from jsonschema import Draft7Validator
    sections = {json.loads(p.read_text())["id"]: (p, json.loads(p.read_text())) for p in sorted((ROOT / "sections").glob("*.json"))}
    prims = {json.loads(p.read_text())["id"]: json.loads(p.read_text()) for p in (ROOT / "primitives").glob("*.json")}
    comps = {json.loads(p.read_text())["id"]: json.loads(p.read_text()) for p in (ROOT / "components").glob("*.json")}

    # 1. closed section-contract schema
    cs = Draft7Validator(load("schema/section-contract.schema.json"))
    errs = [f"{sid}: {list(e.absolute_path)} {e.message[:80]}" for sid, (_, d) in sections.items() for e in cs.iter_errors(d)]
    errs += [f"{p.name} filename != id" for sid, (p, d) in sections.items() if p.stem != sid]
    rec("FAIL" if errs else "PASS", "section contracts closed schema", "; ".join(errs[:3]) or f"{len(sections)} contracts")

    # 2. source / semantic split + source re-read
    errs = []
    for sid, (_, d) in sections.items():
        if d["semantic"]["id"] != sid:
            errs.append(f"{sid}: semantic.id != id")
        if d["source"]["id"] == sid:
            errs.append(f"{sid}: source.id must differ from contract id")
        if d["source"]["citation"] != f"{d['source']['file']}:{d['source']['lines']}":
            errs.append(f"{sid}: citation != file:lines")
    rec("FAIL" if errs else "PASS", "R7 source/semantic split", "; ".join(errs[:3]) or f"{len(sections)}/{len(sections)}")

    src = source_root()
    have_src = (src / "src").is_dir() and (src / "public").is_dir()
    if have_src:
        errs = []
        for sid, (_, d) in sections.items():
            f = src / d["source"]["file"]
            if not f.exists():
                errs.append(f"{sid}: {d['source']['file']} missing")
                continue
            lines = f.read_text().split("\n")
            a, _, b = d["source"]["lines"].partition("-")
            a, b = int(a), int(b or a)
            if b > len(lines):
                errs.append(f"{sid}: lines {a}-{b} beyond {len(lines)}")
                continue
            chunk = "\n".join(lines[a - 1:b])
            if d["source"]["marker"] not in chunk or f"<{d['source']['tag']}" not in chunk:
                errs.append(f"{sid}: tag/marker {d['source']['marker']!r} not at {d['source']['citation']}")
        rec("FAIL" if errs else "PASS", "R7 source re-read (tag+marker at cited line)", "; ".join(errs[:3]) or f"{len(sections)} ranges re-read")
        # every evidence citation in the package
        errs, n = [], 0
        for p in sorted(ROOT.rglob("*.json")):
            for where, ev in iter_evidence(json.loads(p.read_text()), p.relative_to(ROOT).as_posix()):
                n += 1
                path, _, rng = ev["cite"].rpartition(":")
                f = src / path
                if not f.exists():
                    errs.append(f"{where}: {path} missing")
                    continue
                lines = f.read_text().split("\n")
                a, _, b = rng.partition("-")
                a, b = int(a), int(b or a)
                if a < 1 or b < a or b > len(lines):
                    errs.append(f"{where}: {ev['cite']} out of range ({len(lines)} lines)")
                elif ev["expect"] not in "\n".join(lines[a - 1:b]):
                    errs.append(f"{where}: {ev['cite']} does not contain {ev['expect']!r}")
        rec("FAIL" if errs else "PASS", "citation validity (range + expected text)", "; ".join(errs[:3]) or f"{n} citations re-read")
        # foundation colours vs real :root
        css = (src / "public/assets/css/site.css").read_text()
        errs = [f"{tid} {t['value']} not in site.css" for tid, t in load("tokens/00-foundation/color.json")["tokens"].items() if f"{t['cssVar']}:{t['value']}" not in css]
        rec("FAIL" if errs else "PASS", "foundation colours == source :root", "; ".join(errs[:3]) or "23 colours match")
    else:
        rec("WARN", "source re-read / citations", f"no sibling source tree at {src.name or src}; citation checks skipped (standalone package)")

    # 3. allowlist parity
    al = load("tokens/llm/component-allowlist.json")
    man = load("registry.manifest.json")
    schema = load("schema/pagespec.schema.json")
    errs = []
    for kind, have, want in (("sections", set(al["sections"]), set(sections)), ("primitives", set(al["primitives"]), set(prims)), ("components", set(al["components"]), set(comps))):
        if have - want:
            errs.append(f"phantom {kind}: {sorted(have - want)}")
        if want - have:
            errs.append(f"{kind} missing from allowlist: {sorted(want - have)}")
    if sorted(al["nodeProperties"]) != sorted(schema["definitions"]["node"]["properties"]):
        errs.append("nodeProperties != schema node properties")
    roles = load("assets/asset-roles.json")["roles"]
    if sorted(al["assetRoles"]) != sorted(roles):
        errs.append("assetRoles != assets/asset-roles.json")
    pats = load("tokens/00-foundation/motion-patterns.json")["patterns"]
    if sorted(al["motionPatterns"]) != sorted(pats):
        errs.append("motionPatterns != motion-patterns.json")
    for sid, (_, d) in sections.items():
        a = al["sections"].get(sid)
        if a and (a["motionPatterns"] != d["motion"]["allowedPatterns"] or a["category"] != d["semantic"]["category"]):
            errs.append(f"{sid}: allowlist motion/category drift")
    if al["version"] != man.get("allowlistVersion"):
        errs.append(f"allowlistVersion {man.get('allowlistVersion')} != allowlist version {al['version']}")
    rec("FAIL" if errs else "PASS", "allowlist parity", "; ".join(errs[:3]) or f"{len(al['sections'])} sections, {len(al['primitives'])} primitives, {len(al['components'])} components, version {al['version']}")

    # 4. schema parity (regenerated from contracts)
    gen = module("schema/generate_schema.py", "gen")
    same = (ROOT / "schema/pagespec.schema.json").read_text() == gen.dump(gen.build())
    rec("PASS" if same else "FAIL", "schema/contract parity", "pagespec.schema.json == generate_schema.build()" if same else "schema drifted from section contracts; run schema/generate_schema.py --write")
    try:
        Draft7Validator.check_schema(schema)
        rec("PASS", "Draft-07 metaschema", "pagespec.schema.json is a valid Draft-07 schema")
    except Exception as e:
        rec("FAIL", "Draft-07 metaschema", str(e)[:120])

    # 5. templates / contracts / routes
    tpls = load("templates/templates.json")["templates"]
    errs = []
    used = set()
    for tid, t in tpls.items():
        for n in t["nodes"]:
            used.add(n["section"])
            if n["section"] not in sections:
                errs.append(f"{tid}: node {n['section']} has no contract")
            elif sections[n["section"]][1]["region"] != n["region"]:
                errs.append(f"{tid}: {n['section']} region drift")
            if not isinstance(n.get("required"), bool) or not isinstance(n.get("repeatable"), bool):
                errs.append(f"{tid}: {n['section']} required/repeatable must be booleans")
    if set(sections) - used:
        errs.append(f"contracts used by no template: {sorted(set(sections) - used)}")
    routes = load("templates/routes.json")
    seen = {}
    for r in routes["routes"]:
        seen[r["route"]] = seen.get(r["route"], 0) + 1
        if r["template"] not in tpls:
            errs.append(f"route {r['route']} -> unknown template")
    for r in routes["notImplementedByClone"]:
        seen[r["route"]] = seen.get(r["route"], 0) + 1
        if len(r.get("reason", "")) < 30:
            errs.append(f"{r['route']}: omission needs a reason")
    errs += [f"route {k} mapped {v}x" for k, v in seen.items() if v != 1]
    tpl_routes = sorted(x for t in tpls.values() for x in t["routes"])
    if tpl_routes != sorted(r["route"] for r in routes["routes"]):
        errs.append("templates.json routes != routes.json implemented routes")
    rec("FAIL" if errs else "PASS", "templates/contracts/routes mapping", "; ".join(errs[:3]) or f"{len(tpls)} template(s), {len(routes['routes'])} implemented route(s), {len(routes['notImplementedByClone'])} documented as not implemented by the clone, each mapped exactly once")

    # 6. graph <-> validator agreement
    sv = module("schema/semantic_validate.py", "sv")
    gids = {r["id"] for r in load("compatibility/graph.json")["rules"]}
    code = (ROOT / "schema/semantic_validate.py").read_text()
    errs = []
    if gids != sv.GRAPH_RULE_IDS:
        errs.append(f"graph ids {sorted(gids ^ sv.GRAPH_RULE_IDS)} differ from validator GRAPH_RULE_IDS")
    errs += [f"{g} not enforced in validator code" for g in gids if code.count(f'"{g}"') < 2]
    sev = {r["id"]: r["severity"] for r in load("compatibility/graph.json")["rules"]}
    for g, s in sev.items():
        call = "rep.warn" if s == "warn" else "rep.err"
        if f'{call}("{g}"' not in code:
            errs.append(f"{g}: graph severity {s} but validator does not call {call}")
    rec("FAIL" if errs else "PASS", "graph <-> validator agreement", "; ".join(errs[:3]) or f"{len(gids)} rules, ids + severities agree")

    # 7. asset availability pins (R3)
    errs = []
    if PINNED_AVAILABILITY != sv.PINNED_AVAILABILITY:
        errs.append("verify_all PINNED_AVAILABILITY != semantic_validate PINNED_AVAILABILITY")
    for rid, r in roles.items():
        if rid not in PINNED_AVAILABILITY:
            errs.append(f"{rid} has no pin")
        elif r["availability"] != PINNED_AVAILABILITY[rid]:
            errs.append(f"{rid}: registry {r['availability']} != pinned {PINNED_AVAILABILITY[rid]}")
        if r["availability"] != "generation-safe" and not r.get("generationSafeSubstitutes"):
            errs.append(f"{rid}: needs generationSafeSubstitutes")
        for s in r.get("generationSafeSubstitutes", []):
            if PINNED_AVAILABILITY.get(s) != "generation-safe":
                errs.append(f"{rid}: substitute {s} is not generation-safe")
        if "must-reuse-exact" in json.dumps(r):
            errs.append(f"{rid}: must-reuse-exact is never allowed")
    errs += [f"pin {k} has no registry role" for k in PINNED_AVAILABILITY if k not in roles]
    for sid, (_, d) in sections.items():
        for g in d["generatedAssetRoles"]:
            if PINNED_AVAILABILITY.get(g) != "generation-safe":
                errs.append(f"{sid}: generatedAssetRoles has non-generation-safe {g}")
    rec("FAIL" if errs else "PASS", "R3 PINNED_AVAILABILITY", "; ".join(errs[:3]) or f"{len(roles)} roles pinned in code (verify_all == semantic_validate == registry)")

    # 8. retrieval eligibility pin (R8)
    errs = []
    if RETRIEVAL_INELIGIBLE != sv.RETRIEVAL_INELIGIBLE:
        errs.append("verify_all RETRIEVAL_INELIGIBLE != semantic_validate RETRIEVAL_INELIGIBLE")
    for sid, (_, d) in sections.items():
        pinned = sid not in RETRIEVAL_INELIGIBLE
        if d["retrievalEligible"] != pinned:
            errs.append(f"{sid}: contract retrievalEligible {d['retrievalEligible']} != pin {pinned}")
        if al["sections"].get(sid, {}).get("retrievalEligible") != pinned:
            errs.append(f"{sid}: allowlist retrievalEligible != pin")
        if RUNTIME_ID_PATTERN.search(sid + " " + d["title"]) and sid not in RETRIEVAL_INELIGIBLE:
            errs.append(f"{sid}: looks like runtime UI but is not pinned ineligible")
        if not d["retrievalEligible"] and len(d.get("retrievalIneligibleReason", "")) < 30:
            errs.append(f"{sid}: reason < 30 chars")
        if d["region"] == "main" and not d["retrievalEligible"]:
            errs.append(f"{sid}: content region section marked ineligible")
    for cid, c in comps.items():
        if (cid in RETRIEVAL_INELIGIBLE_COMPONENTS) != (c["retrievalEligible"] is False) or al["components"][cid]["retrievalEligible"] != c["retrievalEligible"]:
            errs.append(f"{cid}: component retrievalEligible drift")
    rec("FAIL" if errs else "PASS", "R8 retrievalEligible pin", "; ".join(errs[:3]) or f"{len(RETRIEVAL_INELIGIBLE)} sections + {len(RETRIEVAL_INELIGIBLE_COMPONENTS)} component pinned ineligible")

    # 9. motion wiring
    errs = []
    for sid, (_, d) in sections.items():
        for p in d["motion"]["allowedPatterns"]:
            if p not in pats:
                errs.append(f"{sid}: unknown pattern {p}")
            elif d["motion"]["reducedMotionFallback"].get(p) != pats[p]["reducedMotionFallback"]:
                errs.append(f"{sid}: fallback for {p} drifted")
    lp = pats.get("intro-loader-seal", {})
    if [s["t"] for s in lp.get("timeline", [])] != [0, 0, 850, 1650, 1700, 2050, 2780, 2800, 3700]:
        errs.append("intro-loader-seal timeline offsets drifted from site.js loader()")
    rec("FAIL" if errs else "PASS", "motion patterns wiring", "; ".join(errs[:3]) or f"{len(pats)} patterns; loader timeline offsets 0/0/850/1650/1700/2050/2780/2800/3700ms")

    # 10. token catalog / policy (R10)
    tc = module("extraction/token_catalog.py", "tc")
    errs = []
    if (ROOT / "tokens/llm/token-catalog.json").read_text() != tc.dump(tc.derive()):
        errs.append("token-catalog.json drifted from token files (run extraction/token_catalog.py --write)")
    cat = load("tokens/llm/token-catalog.json")
    pol = load("tokens/llm/token-policy.json")
    cats = set(cat["categories"])
    for prop, sp in pol["styleProperties"].items():
        errs += [f"policy {prop}: category {c} not in catalog" for c in sp["categories"] if c not in cats]
        errs += [f"policy {prop}: id {i} not in catalog" for i in sp.get("allowedIds", []) if i not in cat["tokens"]]
    if sorted(pol["styleProperties"]) != sorted(schema["definitions"]["style"]["properties"]):
        errs.append("policy styleProperties != schema style properties")
    for th, combo in pol["themeCombos"].items():
        if th.startswith("$"):
            continue
        for prop, ids in combo.items():
            errs += [f"themeCombos.{th}.{prop}: {i} not in catalog" for i in ids if i not in cat["tokens"]]
    errs += [f"approvedFontFamilies {f} not a catalog fontFamily" for f in pol["approvedFontFamilies"] if cat["tokens"].get(f, {}).get("category") != "fontFamily"]
    for k in ("token-catalog", "token-policy", "component-allowlist", "motion-patterns"):
        if k not in json.dumps(man.get("entryPoints")):
            errs.append(f"{k} not registered in manifest entryPoints")
    if man.get("tokenCatalog", {}).get("count") != cat["count"] or man.get("tokenCatalog", {}).get("version") != cat["version"]:
        errs.append("manifest tokenCatalog count/version != catalog")
    rec("FAIL" if errs else "PASS", "R10 token catalog/policy", "; ".join(errs[:3]) or f"{cat['count']} catalog tokens in {len(cats)} categories; policy resolves")

    # 11. examples
    repo = sv.Repo(ROOT)
    errs, gen_tpls, info = [], set(), []
    ref_strings = []
    for p in sorted((ROOT / "schema/examples").glob("*.pagespec.json")):
        spec = json.loads(p.read_text())
        try:
            rep = sv.validate(spec, repo)
        except Exception as ex:
            errs.append(f"{p.name}: validator crashed ({type(ex).__name__}: {ex})")
            continue
        if rep.errors:
            errs.append(f"{p.name}: {[(c, pa) for _, c, pa, _ in rep.errors][:3]}")
        if spec["mode"] == "generated":
            gen_tpls.add(spec["template"])
        if ("generated" in p.name) != (spec["mode"] == "generated"):
            errs.append(f"{p.name}: filename/mode mismatch")
        info.append(f"{p.name} ({spec['mode']}) 0 errors" if not rep.errors else f"{p.name} FAIL")
        if spec["mode"] == "reference":
            def w(o):
                if isinstance(o, str):
                    ref_strings.append(o)
                elif isinstance(o, dict):
                    [w(v) for k, v in o.items() if k not in ("assetRole", "src", "href", "url", "kind", "pattern", "reducedMotionFallback", "section", "variant", "region", "theme")]
                elif isinstance(o, list):
                    [w(v) for v in o]
            w(spec["nodes"])
    errs += [f"no generated example for {t}" for t in tpls if t not in gen_tpls]
    corpus = set(load("schema/source-brand.json")["copyCorpus"])
    missing = [s for s in ref_strings if s not in corpus]
    if missing:
        errs.append(f"{len(missing)} reference strings missing from source-brand copyCorpus, e.g. {missing[0][:40]!r}")
    rec("FAIL" if errs else "PASS", "example PageSpecs (Draft-07 + semantic)", "; ".join(errs[:3]) or "; ".join(info))

    # 12. wrapper gate (R9)
    wg = module("extraction/wrapper_gate.py", "wg")
    pinned = {"VIEWPORT_WIDTH": 1440, "HERO_WARN_PX": 1800, "HERO_ERROR_PX": 3000, "SHARE_WARN": 0.50, "SHARE_ERROR": 0.60, "MIN_INFLOW": 3}
    drift = {k: getattr(wg, k, None) for k, v in pinned.items() if getattr(wg, k, None) != v}
    if drift:
        rec("FAIL", "R9 wrapper gate thresholds", f"wrapper_gate thresholds drifted from pinned values: {drift}")
    e, w, i = wg.run(ROOT)
    rec("FAIL" if e else "PASS", "R9 wrapper gate", "; ".join(e[:3]) or ("; ".join(i) + (f"; {len(w)} warning(s)" if w else "; 0 warnings")))

    # 13. manifest entryPoints + counts + README
    errs = []
    eps = man.get("entryPoints", {})
    flat = [v for v in (eps.values() if isinstance(eps, dict) else eps)]
    for v in flat:
        if v.startswith("..") or v.startswith("/") or not (ROOT / v).exists():
            errs.append(f"entryPoint {v} missing or outside package")
    counts = compute_counts()
    if "--write-counts" in sys.argv:
        man["counts"] = counts
        (ROOT / "registry.manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")
        rd = (ROOT / "README.md").read_text()
        rd = re.sub(r"<!-- COUNTS:BEGIN.*?<!-- COUNTS:END -->", readme_block(counts), rd, flags=re.S)
        (ROOT / "README.md").write_text(rd)
    if man.get("counts") != counts:
        diff = {k: (man.get("counts", {}).get(k), v) for k, v in counts.items() if man.get("counts", {}).get(k) != v}
        errs.append(f"manifest counts drift {diff}")
    if readme_block(counts) not in (ROOT / "README.md").read_text():
        errs.append("README counts block != recomputed counts")
    if man.get("productionApproved") is not False or man.get("status") != "design-review-pending":
        errs.append("manifest must stay design-review-pending / productionApproved false")
    rec("FAIL" if errs else "PASS", "manifest entryPoints/counts/README", "; ".join(errs[:3]) or f"{len(flat)} entryPoints inside package; counts recomputed and equal")

    # 14. hygiene
    junk = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.name in JUNK or "__MACOSX" in p.parts or "__pycache__" in p.parts]
    absp = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and p.suffix in (".json", ".md", ".py", ".mjs", ".txt") and ABS_PATH.search(p.read_text(errors="ignore"))]
    rec("FAIL" if junk or absp else "PASS", "R14 hygiene", f"junk={junk[:3]} absolutePaths={absp[:3]}" if junk or absp else "no junk files, no absolute machine paths")



if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main())
