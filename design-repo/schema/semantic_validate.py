#!/usr/bin/env python3
"""Semantic validator for PageSpecs (everything Draft-07 cannot express).

    python3 schema/semantic_validate.py schema/examples/home.generated.pagespec.json [...]

Layers, in order: Draft-07 schema (jsonschema) -> repo pins (asset availability, retrieval
eligibility) -> template cross-check (declared template's real node list: membership, required,
order, region, duplicates, route) -> contract checks (variant, theme, retrievalEligible, motion
pattern + locked reduced-motion fallback, maxWords, asset-role-per-slot) -> compatibility graph
rules -> token policy on node.style -> generated-mode leakage rules (brand, CTA, copy, URL,
asset, person, rating). Exit 1 on any error. Standard library + jsonschema only.
"""
import json, re, sys
sys.dont_write_bytecode = True
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- pins (independent of the registry files)
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
# Runtime / utility UI that must never be retrieved as page content (R8).
RETRIEVAL_INELIGIBLE = {
    "utility.skip-link", "runtime.intro-loader", "utility.scroll-progress",
    "utility.grain-overlay", "runtime.mobile-menu",
}
RUNTIME_ID_PATTERN = re.compile(r"(loader|preload|skip|progress|grain|overlay|mobile-menu|drawer|modal|dialog|toast|cookie|consent|cursor|feedback)", re.I)

GRAPH_RULE_IDS = {"ONE_HERO", "HERO_FIRST_IN_MAIN", "REGION_ORDER", "FOOTER_LAST", "CONVERSION_PRECEDES_FOOTER", "RUNTIME_OUTSIDE_MAIN",
                  "ONE_LOADER", "ONE_PINNED_SCRUB", "AUTOPLAY_BUDGET", "NO_ADJACENT_SAME_CATEGORY", "NO_ADJACENT_NIGHT"}
GENERATED_RULE_IDS = {"GENERATED_MODE_BRAND", "GENERATED_MODE_CTA", "GENERATED_MODE_COPY", "GENERATED_MODE_URL",
                      "GENERATED_MODE_ASSET", "GENERATED_MODE_PERSON", "GENERATED_MODE_RATING"}
TOKEN_RULE_IDS = {"TOKEN_UNKNOWN", "TOKEN_RAW_COLOR", "TOKEN_ARBITRARY_SPACING", "TOKEN_UNSUPPORTED_FONT", "TOKEN_THEME_COMBO", "TOKEN_CATEGORY"}
REGION_ORDER = ["pre-main", "main", "post-main"]
NIGHT = {"night", "night-2"}
AUTOPLAY = {"tilt-scrub-autocycle", "tabs-autoplay"}
RAW_COLOR = re.compile(r"(#[0-9a-f]{3,8}\b|\brgba?\(|\bhsla?\(|\b(red|black|white|green|blue)\b)", re.I)
RAW_LENGTH = re.compile(r"^-?\d+(\.\d+)?(px|rem|em|%|vw|vh)?$|\d(px|rem|em|vw|vh)\b", re.I)
PLACEHOLDER_HOST = re.compile(r"^https?://([a-z0-9-]+\.)*[a-z0-9-]+\.(example|invalid)(/|$|\?|#)", re.I)
PLACEHOLDER_MAIL = re.compile(r"^(mailto:)?[^@\s]+@([a-z0-9-]+\.)*[a-z0-9-]+\.(example|invalid)$", re.I)


def _load(rel):
    return json.loads((ROOT / rel).read_text())


class Repo:
    def __init__(self, root=ROOT):
        global ROOT
        ROOT = Path(root)
        self.schema = _load("schema/pagespec.schema.json")
        self.sections = {json.loads(p.read_text())["id"]: json.loads(p.read_text()) for p in sorted((ROOT / "sections").glob("*.json"))}
        self.templates = _load("templates/templates.json")["templates"]
        self.roles = _load("assets/asset-roles.json")["roles"]
        self.patterns = _load("tokens/00-foundation/motion-patterns.json")["patterns"]
        self.graph = {r["id"]: r for r in _load("compatibility/graph.json")["rules"]}
        self.brand = _load("schema/source-brand.json")
        self.catalog = _load("tokens/llm/token-catalog.json")["tokens"]
        self.policy = _load("tokens/llm/token-policy.json")
        self.allowlist = _load("tokens/llm/component-allowlist.json")
        b = self.brand
        self.rx = {k: [re.compile(p, re.I) for p in b[k]] for k in
                   ("brandPatterns", "domainPatterns", "endpointPatterns", "personPatterns", "organisationPatterns", "ctaPatterns", "statPatterns", "assetFilePatterns")}
        self.cta = {norm(c) for c in b["ctaStrings"]}
        self.generic = set(b["genericAllowlist"])
        k = b["copyShingleWords"]
        self.shingles, self.exact = set(), set()
        for s in b["copyCorpus"]:
            w = words(s)
            if len(w) >= b["copyExactMinWords"]:
                self.exact.add(" ".join(w))
            for i in range(len(w) - k + 1):
                self.shingles.add(" ".join(w[i:i + k]))
        self.k = k


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(words(s))


def words(s):
    s = s.lower().replace("’", "'")
    toks = (w.strip(".'") for w in re.split(r"[^a-z0-9₹%+'.]+", s))  # keep 2.5 / 48.2, drop sentence punctuation
    return [w for w in toks if re.search(r"[a-z0-9]", w)]


def count_words(s):
    return len([w for w in s.split() if re.search(r"\w", w)])


class Report:
    def __init__(self):
        self.items = []

    def err(self, code, path, msg):
        self.items.append(("error", code, path, msg))

    def warn(self, code, path, msg):
        self.items.append(("warn", code, path, msg))

    @property
    def errors(self):
        return [i for i in self.items if i[0] == "error"]

    def codes(self, sev="error"):
        return {i[1] for i in self.items if i[0] == sev}


# ---------------------------------------------------------------- repo integrity (pins vs registries)
def repo_pin_errors(repo, rep):
    for rid, r in repo.roles.items():
        if rid not in PINNED_AVAILABILITY:
            rep.err("ASSET_PIN_MISSING", f"assets/asset-roles.json:{rid}", "role has no PINNED_AVAILABILITY entry")
        elif r.get("availability") != PINNED_AVAILABILITY[rid]:
            rep.err("ASSET_PIN_DRIFT", f"assets/asset-roles.json:{rid}", f"availability {r.get('availability')!r} != pinned {PINNED_AVAILABILITY[rid]!r}")
    for rid in PINNED_AVAILABILITY:
        if rid not in repo.roles:
            rep.err("ASSET_PIN_ORPHAN", rid, "pinned role missing from registry")
    for sid, s in repo.sections.items():
        pinned = sid not in RETRIEVAL_INELIGIBLE
        if s.get("retrievalEligible", True) != pinned:
            rep.err("RETRIEVAL_PIN", f"sections/{sid}.json", f"retrievalEligible={s.get('retrievalEligible')} contradicts pin ({pinned})")
        al = repo.allowlist["sections"].get(sid, {})
        if al.get("retrievalEligible", True) != pinned:
            rep.err("RETRIEVAL_PIN", f"tokens/llm/component-allowlist.json:{sid}", "allowlist retrievalEligible contradicts pin")
        if RUNTIME_ID_PATTERN.search(sid + " " + s.get("title", "")) and sid not in RETRIEVAL_INELIGIBLE:
            rep.err("RETRIEVAL_PIN", f"sections/{sid}.json", "id/title looks like runtime UI but is not in RETRIEVAL_INELIGIBLE")


# ---------------------------------------------------------------- content walking
def walk_content(spec_f, val, path, rep, out):
    """Check maxWords / media roles; collect (path, kind, value, field) for later rules."""
    t = spec_f["type"]
    if val is None:
        return
    if t == "text" and isinstance(val, str):
        if count_words(val) > spec_f["maxWords"]:
            rep.err("MAX_WORDS", path, f"{count_words(val)} words > maxWords {spec_f['maxWords']}")
        out.append((path, "text", val, spec_f))
    elif t in ("href", "email") and isinstance(val, str):
        out.append((path, t, val, spec_f))
    elif t == "media" and isinstance(val, dict):
        role = val.get("assetRole")
        if role not in spec_f["assetRoles"]:
            rep.err("ASSET_ROLE_NOT_ALLOWED", path, f"{role!r} not allowed in this slot {spec_f['assetRoles']}")
        out.append((path, "media", val, spec_f))
        if isinstance(val.get("alt"), str):
            out.append((path + ".alt", "text", val["alt"], {"type": "text"}))
        if isinstance(val.get("src"), str):
            out.append((path + ".src", "src", val["src"], spec_f))
    elif t == "enum" and isinstance(val, str):
        out.append((path, "enum", val, spec_f))
    elif t == "object" and isinstance(val, dict):
        for k, f in spec_f["fields"].items():
            walk_content(f, val.get(k), f"{path}.{k}", rep, out)
        if set(spec_f["fields"]) >= {"name", "role", "isFictional"}:
            out.append((path, "person", val, spec_f))
    elif t == "list" and isinstance(val, list):
        for i, v in enumerate(val):
            walk_content(spec_f["items"], v, f"{path}[{i}]", rep, out)


# ---------------------------------------------------------------- main validation
def validate(spec, repo=None, with_schema=True):
    repo = repo or Repo()
    rep = Report()
    if with_schema:
        try:
            from jsonschema import Draft7Validator
        except ImportError:
            rep.err("SCHEMA_VALIDATOR_MISSING", "-", "pip install jsonschema (Draft-07 layer is mandatory)")
            return rep
        for e in Draft7Validator(repo.schema).iter_errors(spec):
            rep.err("SCHEMA", "/".join(str(p) for p in e.absolute_path) or "$", e.message[:200])
        if rep.errors:
            return rep
    repo_pin_errors(repo, rep)

    mode = spec.get("mode")
    tid = spec.get("template")
    tpl = repo.templates.get(tid)
    nodes = spec.get("nodes", [])
    if not tpl:
        rep.err("TEMPLATE_UNKNOWN", "template", f"{tid!r} not in templates.json")
        return rep
    if spec.get("route") not in tpl["routes"]:
        rep.err("TEMPLATE_ROUTE", "route", f"{spec.get('route')!r} is not a route of {tid} {tpl['routes']}")

    # --- template cross-check against the template's REAL node list
    tnodes = tpl["nodes"]
    tindex = {n["section"]: i for i, n in enumerate(tnodes)}
    seen, last = {}, -1
    for i, n in enumerate(nodes):
        sid = n["section"]
        if sid not in tindex:
            rep.err("TEMPLATE_EXTRA_NODE", f"nodes[{i}]", f"{sid} is not a node of {tid}")
            continue
        tn = tnodes[tindex[sid]]
        seen[sid] = seen.get(sid, 0) + 1
        if seen[sid] > 1 and not tn["repeatable"]:
            rep.err("TEMPLATE_DUPLICATE", f"nodes[{i}]", f"{sid} is not repeatable in {tid}")
        if tindex[sid] < last:
            rep.err("TEMPLATE_ORDER", f"nodes[{i}]", f"{sid} is out of the order defined by {tid}")
        last = max(last, tindex[sid])
        if n["region"] != tn["region"]:
            rep.err("TEMPLATE_REGION", f"nodes[{i}].region", f"{sid} belongs to region {tn['region']}, got {n['region']}")
    for tn in tnodes:
        if tn["required"] and tn["section"] not in seen:
            rep.err("TEMPLATE_MISSING_REQUIRED", "nodes", f"required node {tn['section']} of {tid} is missing")

    # --- per-node contract checks
    collected = []
    for i, n in enumerate(nodes):
        sid = n["section"]
        c = repo.sections.get(sid)
        if not c:
            continue
        p = f"nodes[{i}]"
        if n["variant"] not in c["variants"]:
            rep.err("VARIANT_UNKNOWN", p + ".variant", f"{n['variant']!r} not in {c['variants']}")
        if n["theme"] not in c["themes"]:
            rep.err("THEME_NOT_ALLOWED", p + ".theme", f"{n['theme']!r} not in {c['themes']}")
        pinned = sid not in RETRIEVAL_INELIGIBLE
        if n["retrievalEligible"] != pinned:
            rep.err("RETRIEVAL_PIN", p + ".retrievalEligible", f"{sid} retrievalEligible must be {pinned} (pinned)")
        if n["retrievalEligible"] != c["retrievalEligible"]:
            rep.err("RETRIEVAL_CONTRACT", p + ".retrievalEligible", "differs from section contract")
        m = n["motion"]
        if m["pattern"] not in repo.patterns:
            rep.err("MOTION_NOT_ALLOWED", p + ".motion.pattern", f"{m['pattern']} is not a known motion pattern")
        elif m["pattern"] not in c["motion"]["allowedPatterns"]:
            rep.err("MOTION_NOT_ALLOWED", p + ".motion.pattern", f"{m['pattern']} not allowed for {sid}")
        elif m["reducedMotionFallback"] != repo.patterns[m["pattern"]]["reducedMotionFallback"]:
            rep.err("MOTION_FALLBACK", p + ".motion.reducedMotionFallback", f"{m['pattern']} requires {repo.patterns[m['pattern']]['reducedMotionFallback']!r}")
        local = []
        for k, f in c["content"].items():
            walk_content(f, n["content"].get(k), f"{p}.content.{k}", rep, local)
        collected += [x + (sid,) for x in local]
        if "style" in n:
            check_style(n, p, repo, rep)

    graph_rules(spec, nodes, repo, rep)
    if mode == "generated":
        generated_rules(spec, collected, repo, rep)
    return rep


def check_style(n, p, repo, rep):
    pol = repo.policy
    combos = pol["themeCombos"].get(n["theme"], {})
    for prop, val in n["style"].items():
        sp = pol["styleProperties"][prop]
        path = f"{p}.style.{prop}"
        if RAW_COLOR.search(val):
            rep.err("TOKEN_RAW_COLOR", path, f"raw colour {val!r}; use a token id")
            continue
        if RAW_LENGTH.search(val):
            rep.err("TOKEN_ARBITRARY_SPACING", path, f"raw length {val!r}; use a spacing token")
            continue
        if prop == "displayFont" and val not in pol["approvedFontFamilies"]:
            rep.err("TOKEN_UNSUPPORTED_FONT", path, f"{val!r} not in {pol['approvedFontFamilies']}")
            continue
        tok = repo.catalog.get(val)
        if not tok:
            rep.err("TOKEN_UNKNOWN", path, f"{val!r} not in tokens/llm/token-catalog.json")
            continue
        if tok["category"] not in sp["categories"] or ("allowedIds" in sp and val not in sp["allowedIds"]):
            rep.err("TOKEN_CATEGORY", path, f"{val!r} (category {tok['category']}) not allowed for style.{prop}")
            continue
        if prop in ("surface", "text", "accent") and val not in combos.get(prop, []):
            rep.err("TOKEN_THEME_COMBO", path, f"{val!r} not allowed with theme {n['theme']!r}")


def graph_rules(spec, nodes, repo, rep):
    nodes = [n for n in nodes if n.get("section") in repo.sections]  # unknown ids already reported
    cat = lambda n: repo.sections[n["section"]]["semantic"]["category"]
    main = [n for n in nodes if n["region"] == "main"]
    heroes = [i for i, n in enumerate(nodes) if cat(n) == "HERO"]
    if len(heroes) != 1:
        rep.err("ONE_HERO", "nodes", f"{len(heroes)} HERO nodes; exactly one required")
    if main and cat(main[0]) != "HERO":
        rep.err("HERO_FIRST_IN_MAIN", "nodes", f"first main node is {main[0]['section']}, not the hero")
    ri = [REGION_ORDER.index(n["region"]) for n in nodes]
    if ri != sorted(ri):
        rep.err("REGION_ORDER", "nodes", "regions must run pre-main -> main -> post-main")
    if nodes and nodes[-1]["section"] != "shell.footer":
        rep.err("FOOTER_LAST", "nodes", "shell.footer must be the last node")
    if main and main[-1]["section"] != "conversion.demo-form":
        rep.err("CONVERSION_PRECEDES_FOOTER", "nodes", f"last main node is {main[-1]['section']}, expected conversion.demo-form")
    for i, n in enumerate(nodes):
        if not n["retrievalEligible"] and n["region"] != "pre-main":
            rep.err("RUNTIME_OUTSIDE_MAIN", f"nodes[{i}]", f"runtime/utility node {n['section']} must be in pre-main")
    loaders = [i for i, n in enumerate(nodes) if n["section"] == "runtime.intro-loader"]
    navs = [i for i, n in enumerate(nodes) if n["section"] == "shell.navbar"]
    if len(loaders) > 1 or (loaders and navs and loaders[0] > navs[0]):
        rep.err("ONE_LOADER", "nodes", "at most one intro loader, placed before shell.navbar")
    if sum(1 for n in nodes if n["motion"]["pattern"] == "pinned-scrub-timeline") > 1:
        rep.err("ONE_PINNED_SCRUB", "nodes", "more than one pinned-scrub-timeline")
    if sum(1 for n in nodes if n["motion"]["pattern"] in AUTOPLAY) > 2:
        rep.warn("AUTOPLAY_BUDGET", "nodes", "more than two autoplay patterns")
    for a, b in zip(main, main[1:]):
        if cat(a) == cat(b):
            rep.warn("NO_ADJACENT_SAME_CATEGORY", b["section"], f"{a['section']} and {b['section']} share category {cat(a)}")
    for a, b in zip(nodes, nodes[1:]):
        if a["theme"] in NIGHT and b["theme"] in NIGHT and (a["section"], b["section"]) != ("conversion.demo-form", "shell.footer") \
                and a["region"] != "pre-main" and b["region"] != "pre-main":
            rep.warn("NO_ADJACENT_NIGHT", b["section"], f"{a['section']} -> {b['section']} are both night")


def generated_rules(spec, collected, repo, rep):
    rx = repo.rx
    texts = [(x[0], x[2]) for x in collected if x[1] in ("text", "enum")]
    texts += [("meta.title", spec["meta"]["title"]), ("meta.brandName", spec["meta"]["brandName"])]
    if spec["meta"].get("description"):
        texts.append(("meta.description", spec["meta"]["description"]))
    if not spec["meta"].get("isFictionalBrand"):
        rep.err("GENERATED_MODE_BRAND", "meta.isFictionalBrand", "generated pages must declare a fictional/new brand")
    for path, s in texts:
        if any(r.search(s) for r in rx["brandPatterns"]):
            rep.err("GENERATED_MODE_BRAND", path, f"source brand in {s[:60]!r}")
        if any(r.search(s) for r in rx["personPatterns"] + rx["organisationPatterns"]):
            rep.err("GENERATED_MODE_PERSON", path, f"real person/customer identity in {s[:60]!r}")
        if any(r.search(s) for r in rx["statPatterns"]):
            rep.err("GENERATED_MODE_RATING", path, f"source result/statistic in {s[:60]!r}")
        if any(r.search(s) for r in rx["domainPatterns"]):
            rep.err("GENERATED_MODE_URL", path, f"source domain in {s[:60]!r}")
        if norm(s) in repo.cta or any(r.search(s) for r in rx["ctaPatterns"]):
            rep.err("GENERATED_MODE_CTA", path, f"source CTA {s[:60]!r}")
        w = words(s)
        j = " ".join(w)
        if j and j not in repo.generic and (j in repo.exact or any(" ".join(w[i:i + repo.k]) in repo.shingles for i in range(len(w) - repo.k + 1))):
            rep.err("GENERATED_MODE_COPY", path, f"source copy reused: {s[:60]!r}")
    for x in collected:
        path, kind, val = x[0], x[1], x[2]
        sid = x[4] if len(x) > 4 else None
        if kind in ("href", "email"):
            ok = val.startswith("#") or PLACEHOLDER_HOST.match(val) or PLACEHOLDER_MAIL.match(val)
            if not ok or any(r.search(val) for r in rx["domainPatterns"] + rx["endpointPatterns"]):
                rep.err("GENERATED_MODE_URL", path, f"{val!r} is not an in-page anchor or reserved .example/.invalid placeholder")
        elif kind == "media":
            role = val.get("assetRole")
            if PINNED_AVAILABILITY.get(role) != "generation-safe":
                rep.err("GENERATED_MODE_ASSET", path, f"{role} is {PINNED_AVAILABILITY.get(role)} (pinned); not usable in generated mode")
            elif sid and role not in repo.sections[sid]["generatedAssetRoles"]:
                rep.err("GENERATED_MODE_ASSET", path, f"{role} not in {sid}.generatedAssetRoles")
        elif kind == "src":
            if any(r.search(val) for r in rx["assetFilePatterns"]):
                rep.err("GENERATED_MODE_ASSET", path, f"source asset file {val!r}")
        elif kind == "enum" and val.startswith("endpoint.") and PINNED_AVAILABILITY.get(val) != "generation-safe":
            rep.err("GENERATED_MODE_ASSET", path, f"{val} is a live source endpoint")
        elif kind == "person":
            if val.get("isFictional") is not True:
                rep.err("GENERATED_MODE_PERSON", path, "person in a generated page must be flagged isFictional=true")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    repo, bad = Repo(), 0
    for f in argv:
        spec = json.loads(Path(f).read_text())
        rep = validate(spec, repo)
        e = rep.errors
        w = [i for i in rep.items if i[0] == "warn"]
        print(f"{f}: {len(e)} error(s), {len(w)} warning(s) [mode={spec.get('mode')}]")
        for sev, code, path, msg in rep.items:
            print(f"  {sev.upper():5} {code:28} {path}: {msg}")
        bad += bool(e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
