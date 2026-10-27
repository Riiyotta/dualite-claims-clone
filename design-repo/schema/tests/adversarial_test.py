#!/usr/bin/env python3
"""Adversarial suite: every mutation must be rejected with its expected rule code, every control
must pass. Covers schema layer, template cross-check, retrieval pins (node / contract / allowlist),
asset availability, generated-mode leakage (brand, CTA, copy, URL, asset, person, rating; with the
intro-loader strings called out), token policy, and the wrapper-height gate.

    python3 schema/tests/adversarial_test.py
"""
import copy, json, shutil, sys, tempfile, importlib.util
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def _mod(rel, name):
    s = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def _ex(name):
    return json.loads((ROOT / "schema/examples" / f"home.{name}.pagespec.json").read_text())


def idx(spec, sid):
    return next(i for i, n in enumerate(spec["nodes"]) if n["section"] == sid)


def node(spec, sid):
    return spec["nodes"][idx(spec, sid)]


def C(spec, sid):
    return node(spec, sid)["content"]


def swap(spec, a, b):
    i, j = idx(spec, a), idx(spec, b)
    spec["nodes"][i], spec["nodes"][j] = spec["nodes"][j], spec["nodes"][i]


def setp(path, value):
    def f(s):
        cur = s
        for k in path[:-1]:
            cur = cur[k]
        cur[path[-1]] = value
    return f


def M(name, base, fn, expect, schema=True, kind="spec", sev="error"):
    return {"name": name, "base": base, "fn": fn, "expect": expect, "schema": schema, "kind": kind, "sev": sev}


def _del(s, sid):
    del s["nodes"][idx(s, sid)]


MUTATIONS = [
    # ---- schema layer
    M("mode outside enum", "generated", setp(["mode"], "draft"), "SCHEMA"),
    M("mode missing", "generated", lambda s: s.pop("mode"), "SCHEMA"),
    M("invented template", "generated", setp(["template"], "template.landing"), "SCHEMA"),
    M("invented section alias", "generated", lambda s: node(s, "hero.claims-intro").update(section="hero.marketing"), "SCHEMA"),
    M("missing reducedMotionFallback", "generated", lambda s: node(s, "hero.claims-intro")["motion"].pop("reducedMotionFallback"), "SCHEMA"),
    M("invented motion field", "generated", lambda s: node(s, "hero.claims-intro")["motion"].update(inventedAnimation="spin"), "SCHEMA"),
    M("invented content field", "generated", lambda s: C(s, "hero.claims-intro").update(badge="New"), "SCHEMA"),
    M("invented assetRole", "generated", lambda s: C(s, "hero.claims-intro").update(scene={"assetRole": "image"}), "SCHEMA"),
    M("invented style property", "generated", lambda s: node(s, "hero.claims-intro").update(style={"shadow": "elevation.card"}), "SCHEMA"),
    M("wrong pageSpecVersion", "generated", setp(["pageSpecVersion"], "0.9.0"), "SCHEMA"),
    M("unknown variant", "generated", lambda s: node(s, "faq.accordion").update(variant="exclusive"), "SCHEMA"),
    M("loader flipped eligible (schema layer)", "generated", lambda s: node(s, "runtime.intro-loader").update(retrievalEligible=True), "SCHEMA"),
    # ---- template cross-check (semantic)
    M("duplicate hero", "generated", lambda s: s["nodes"].insert(idx(s, "hero.claims-intro") + 1, copy.deepcopy(node(s, "hero.claims-intro"))), "TEMPLATE_DUPLICATE"),
    M("duplicate hero breaks ONE_HERO", "generated", lambda s: s["nodes"].insert(idx(s, "hero.claims-intro") + 1, copy.deepcopy(node(s, "hero.claims-intro"))), "ONE_HERO"),
    M("required faq removed", "generated", lambda s: _del(s, "faq.accordion"), "TEMPLATE_MISSING_REQUIRED"),
    M("proof/problem reordered", "generated", lambda s: swap(s, "proof.quote-logos", "content.problem-costs"), "TEMPLATE_ORDER"),
    M("section not in template", "generated", lambda s: s["nodes"].insert(7, dict(copy.deepcopy(node(s, "proof.quote-logos")), section="pricing.tiers")), "TEMPLATE_EXTRA_NODE", schema=False),
    M("route not served by template", "generated", setp(["route"], "/pricing"), "TEMPLATE_ROUTE"),
    M("footer moved into main region", "generated", lambda s: node(s, "shell.footer").update(region="main"), "TEMPLATE_REGION", schema=False),
    M("footer not last", "generated", lambda s: swap(s, "shell.footer", "conversion.demo-form"), "FOOTER_LAST"),
    M("loader after navbar", "generated", lambda s: swap(s, "runtime.intro-loader", "shell.navbar"), "ONE_LOADER"),
    M("hero not first in main", "generated", lambda s: swap(s, "hero.claims-intro", "proof.quote-logos"), "HERO_FIRST_IN_MAIN"),
    M("conversion not last in main", "generated", lambda s: swap(s, "faq.accordion", "conversion.demo-form"), "CONVERSION_PRECEDES_FOOTER"),
    M("second pinned scrub (schema)", "generated", lambda s: node(s, "features.platform-tabs")["motion"].update(pattern="pinned-scrub-timeline", reducedMotionFallback="scrub-true-no-smoothing"), "SCHEMA"),
    M("second pinned scrub (semantic)", "generated", lambda s: node(s, "features.platform-tabs")["motion"].update(pattern="pinned-scrub-timeline", reducedMotionFallback="scrub-true-no-smoothing"), "ONE_PINNED_SCRUB", schema=False),
    M("motion pattern not allowed", "generated", lambda s: node(s, "faq.accordion")["motion"].update(pattern="tabs-autoplay", reducedMotionFallback="static-manual-tabs"), "MOTION_NOT_ALLOWED", schema=False),
    M("wrong reduced-motion fallback", "generated", lambda s: node(s, "runtime.intro-loader")["motion"].update(reducedMotionFallback="final-state"), "MOTION_FALLBACK"),
    M("theme not allowed (results on paper)", "generated", lambda s: node(s, "metrics.results-band").update(theme="paper"), "THEME_NOT_ALLOWED", schema=False),
    M("maxWords overflow hero headline", "generated", lambda s: C(s, "hero.claims-intro").update(headline="Drop every single invoice you have into the tray right now please"), "MAX_WORDS"),
    M("maxWords overflow loader fileTag", "generated", lambda s: C(s, "runtime.intro-loader").update(fileTag="Batch 042 sample file opened and queued for the finance review today"), "MAX_WORDS"),
    # ---- retrieval eligibility (R8): node / contract / allowlist / content section
    M("loader flipped eligible (node, semantic)", "generated", lambda s: node(s, "runtime.intro-loader").update(retrievalEligible=True), "RETRIEVAL_PIN", schema=False),
    M("mobile menu moved into main", "generated", lambda s: node(s, "runtime.mobile-menu").update(region="main"), "RUNTIME_OUTSIDE_MAIN", schema=False),
    M("contract flips loader eligible", "generated", lambda r: _edit(r, "sections/runtime.intro-loader.json", lambda d: d.update(retrievalEligible=True)), "RETRIEVAL_PIN", kind="repo"),
    M("allowlist flips loader eligible", "generated", lambda r: _edit(r, "tokens/llm/component-allowlist.json", lambda d: d["sections"]["runtime.intro-loader"].update(retrievalEligible=True)), "RETRIEVAL_PIN", kind="repo"),
    M("content section (hero) marked ineligible", "generated", lambda r: _edit(r, "sections/hero.claims-intro.json", lambda d: d.update(retrievalEligible=False)), "RETRIEVAL_PIN", kind="repo"),
    # ---- asset availability (R3) + proprietary media
    M("registry loosens real logo", "generated", lambda r: _edit(r, "assets/asset-roles.json", lambda d: d["roles"]["brand.logo-source"].update(availability="generation-safe")), "ASSET_PIN_DRIFT", kind="repo"),
    M("asset role not allowed in slot", "generated", lambda s: C(s, "hero.claims-intro").update(scene={"assetRole": "logo.customer-placeholder"}), "ASSET_ROLE_NOT_ALLOWED", schema=False),
    M("generated nav uses real logo", "generated", lambda s: C(s, "shell.navbar").update(brandMark={"assetRole": "brand.logo-source", "src": "/logo-dark.png"}), "GENERATED_MODE_ASSET"),
    M("generated platform uses product screenshot", "generated", lambda s: C(s, "features.platform-tabs")["tabs"][0].update(image={"assetRole": "screenshot.platform-source", "src": "/validate.webp"}), "GENERATED_MODE_ASSET"),
    M("generated story reuses testimonial video", "generated", lambda s: C(s, "proof.video-story").update(video={"assetRole": "video.testimonial-source", "src": "/testimonial.mp4"}), "GENERATED_MODE_ASSET"),
    M("generated safe role but source file", "generated", lambda s: C(s, "features.platform-tabs")["tabs"][1].update(image={"assetRole": "image.generated-product-visual", "src": "/stamp.webp"}), "GENERATED_MODE_ASSET"),
    M("generated trust reuses brand animation", "generated", lambda s: C(s, "trust.guarantees").update(media={"assetRole": "video.trust-animation-source", "src": "/trust-anim.mp4"}), "GENERATED_MODE_ASSET"),
    M("generated form posts to live endpoint", "generated", lambda s: C(s, "conversion.demo-form")["form"].update(endpoint={"assetRole": "endpoint.lead-source", "url": "/api/lead"}), "GENERATED_MODE_ASSET"),
    M("generated form endpoint url leak", "generated", lambda s: C(s, "conversion.demo-form")["form"]["endpoint"].update(url="/api/lead"), "GENERATED_MODE_URL"),
    M("generated customer logo is real mark", "generated", lambda s: C(s, "proof.quote-logos")["logos"][0].update(mark={"assetRole": "logo.customer-source"}), "GENERATED_MODE_ASSET"),
    # ---- intro loader leakage (generation-safe variant must stay generic)
    M("loader seal uses source mark", "generated", lambda s: C(s, "runtime.intro-loader").update(sealMark={"assetRole": "mark.seal-source"}), "GENERATED_MODE_ASSET"),
    M("loader brand label = source brand", "generated", lambda s: C(s, "runtime.intro-loader").update(brandLabel="Dualite Claims"), "GENERATED_MODE_BRAND"),
    M("loader ring text = source ring (brand)", "generated", lambda s: C(s, "runtime.intro-loader").update(sealRingText="DUALITE CLAIMS · CHECKED · SEALED · FILED ·"), "GENERATED_MODE_BRAND"),
    M("loader ring text = source ring (copy)", "generated", lambda s: C(s, "runtime.intro-loader").update(sealRingText="DUALITE CLAIMS · CHECKED · SEALED · FILED ·"), "GENERATED_MODE_COPY"),
    M("loader file tag = source file tag", "generated", lambda s: C(s, "runtime.intro-loader").update(fileTag="Claim 1187 · RGHS · OPD"), "GENERATED_MODE_COPY"),
    M("loader status = source status (stat)", "generated", lambda s: C(s, "runtime.intro-loader")["statusSteps"][1].update(text="Checking 50+ case rules"), "GENERATED_MODE_RATING"),
    M("loader foot label = source foot label", "generated", lambda s: C(s, "runtime.intro-loader").update(footLabel="ECHS · RGHS · OPD · IPD"), "GENERATED_MODE_COPY"),
    M("loader status = source opening line", "generated", lambda s: C(s, "runtime.intro-loader")["statusSteps"][0].update(text="Opening claim file"), "GENERATED_MODE_COPY"),
    # ---- brand / CTA / copy / URL / person / rating
    M("brandName = source product", "generated", setp(["meta", "brandName"], "ClaimIt by Dualite"), "GENERATED_MODE_BRAND"),
    M("isFictionalBrand false", "generated", setp(["meta", "isFictionalBrand"], False), "GENERATED_MODE_BRAND"),
    M("product feature name leak", "generated", lambda s: C(s, "features.platform-tabs")["tabs"][2].update(title="Digistamp"), "GENERATED_MODE_BRAND"),
    M("hero headline = source", "generated", lambda s: C(s, "hero.claims-intro").update(headline="Scan the file."), "GENERATED_MODE_COPY"),
    M("hero sub copies a source sentence", "generated", lambda s: C(s, "hero.claims-intro").update(sub="Our tool reads every scanned claim file, checks it against the rules, and your team approves before anything is final."), "GENERATED_MODE_COPY"),
    M("faq answer copied", "generated", lambda s: C(s, "faq.accordion")["items"][0].update(answer="No. Your team keeps scanning the way it does today."), "GENERATED_MODE_COPY"),
    M("nav CTA = source CTA", "generated", lambda s: C(s, "shell.navbar")["cta"].update(label="Book a demo"), "GENERATED_MODE_CTA"),
    M("hero CTA = source CTA", "generated", lambda s: C(s, "hero.claims-intro")["primaryCta"].update(label="Book a 30-minute demo"), "GENERATED_MODE_CTA"),
    M("CTA pattern Try <Brand>", "generated", lambda s: C(s, "hero.claims-intro")["secondaryCta"].update(label="Try Dualite free"), "GENERATED_MODE_CTA"),
    M("source domain link", "generated", lambda s: C(s, "shell.navbar")["links"][0].update(href="https://claims.dualite.dev/"), "GENERATED_MODE_URL"),
    M("source blog path", "generated", lambda s: C(s, "shell.footer")["columns"][0]["links"][0].update(href="/blog/"), "GENERATED_MODE_URL"),
    M("source contact email", "generated", lambda s: C(s, "runtime.mobile-menu").update(contactEmail="info@dualite.dev"), "GENERATED_MODE_URL"),
    M("non-placeholder external URL", "generated", lambda s: C(s, "shell.footer")["columns"][1]["links"][0].update(href="https://fernwick.com/about"), "GENERATED_MODE_URL"),
    M("real customer person", "generated", lambda s: C(s, "proof.quote-logos")["attribution"].update(name="Mayank Singhi"), "GENERATED_MODE_PERSON"),
    M("person not flagged fictional", "generated", lambda s: C(s, "proof.video-story")["speaker"].pop("isFictional"), "GENERATED_MODE_PERSON"),
    M("real customer organisation", "generated", lambda s: C(s, "proof.quote-logos")["logos"][0].update(name="Medipulse Hospital"), "GENERATED_MODE_PERSON"),
    M("source result 48%", "generated", lambda s: C(s, "metrics.results-band")["metrics"][0].update(value="48%"), "GENERATED_MODE_RATING"),
    M("source result 7 -> 3 days", "generated", lambda s: C(s, "editorial.case-study")["results"][0].update(value="7 → 3 days"), "GENERATED_MODE_RATING"),
    # ---- token policy (R10)
    M("raw hex accent", "generated", lambda s: node(s, "hero.claims-intro").update(style={"accent": "#3D5A2A"}), "TOKEN_RAW_COLOR"),
    M("raw rgb accent", "generated", lambda s: node(s, "hero.claims-intro").update(style={"accent": "rgb(61,90,42)"}), "TOKEN_RAW_COLOR"),
    M("arbitrary spacing", "generated", lambda s: node(s, "hero.claims-intro").update(style={"paddingBlock": "120px"}), "TOKEN_ARBITRARY_SPACING"),
    M("unsupported font", "generated", lambda s: node(s, "hero.claims-intro").update(style={"displayFont": "Inter"}), "TOKEN_UNSUPPORTED_FONT"),
    M("unknown token", "generated", lambda s: node(s, "hero.claims-intro").update(style={"surface": "surface.marble"}), "TOKEN_UNKNOWN"),
    M("token of wrong category", "generated", lambda s: node(s, "hero.claims-intro").update(style={"paddingBlock": "space.12"}), "TOKEN_CATEGORY"),
    M("paper surface on night theme", "generated", lambda s: node(s, "conversion.demo-form").update(style={"surface": "surface.paper"}), "TOKEN_THEME_COMBO"),
    M("ink text on night theme", "generated", lambda s: node(s, "conversion.demo-form").update(style={"text": "text.primary"}), "TOKEN_THEME_COMBO"),
    # ---- wrapper gate (R9)
    M("HERO 1900px warns", None, lambda mv, wl: _h(mv, "hero.claims-intro", 1900), "HERO 1800px", kind="gate", sev="warn"),
    M("HERO 3100px fails", None, lambda mv, wl: _h(mv, "hero.claims-intro", 3100), "HERO 3000px", kind="gate"),
    M("majority-share section fails", None, lambda mv, wl: _h(mv, "features.pinned-workflow", 30000), "60% share", kind="gate"),
    M("whitelist without justification", None, lambda mv, wl: (_h(mv, "features.pinned-workflow", 30000), wl["entries"].append({"route": "/", "section": "features.pinned-workflow", "kind": "share", "reviewedBy": "design lead", "justification": "pin", "maxHeightPx": 40000})), "justification", kind="gate"),
    M("agent whitelist without attestation phrase", None, lambda mv, wl: (_h(mv, "features.pinned-workflow", 30000), wl["entries"].append({"route": "/", "section": "features.pinned-workflow", "kind": "share", "reviewedBy": "build agent", "justification": "Pinned workflow is one semantic walkthrough unit.", "maxHeightPx": 40000})), "agent attestation", kind="gate"),
    M("whitelist cap below measured height", None, lambda mv, wl: (_h(mv, "features.pinned-workflow", 30000), wl["entries"].append({"route": "/", "section": "features.pinned-workflow", "kind": "share", "reviewedBy": "design lead", "justification": "Pinned workflow is one semantic walkthrough unit.", "maxHeightPx": 20000})), "exceeds maxHeightPx", kind="gate"),
    M("stale whitelist entry", None, lambda mv, wl: wl["entries"].append({"route": "/", "section": "faq.accordion", "kind": "share", "reviewedBy": "design lead", "justification": "FAQ is a long list of questions on this page.", "maxHeightPx": 5000}), "stale whitelist", kind="gate"),
    M("missing measurement", None, lambda mv, wl: mv["sectionHeights"]["pages"]["/"]["live"]["sections"].pop("faq.accordion"), "missing measurement", kind="gate"),
    M("measured at wrong viewport", None, lambda mv, wl: mv["sectionHeights"]["viewport"].update(width=1280), "gate requires 1440", kind="gate"),
]


def _h(mv, sid, h):
    mv["sectionHeights"]["pages"]["/"]["live"]["sections"][sid]["height"] = h


def _edit(root, rel, fn):
    p = Path(root) / rel
    d = json.loads(p.read_text())
    fn(d)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))


CONTROLS = [
    ("reference example passes (real brand, copy, assets allowed in reference mode)", "reference", lambda s: None),
    ("generated example passes (zero source identity)", "generated", lambda s: None),
    ("generated page without the optional intro loader passes", "generated", lambda s: _del(s, "runtime.intro-loader")),
    ("generated page without the optional grain overlay passes", "generated", lambda s: _del(s, "utility.grain-overlay")),
    ("generated loader with different generic ring text passes", "generated", lambda s: C(s, "runtime.intro-loader").update(sealRingText="RECEIVED · VERIFIED · SENT ·", brandLabel="Northwind Papers")),
    ("reference cta -> footer night adjacency is a named exception (no warning)", "reference", lambda s: None),
    ("wrapper gate passes on real measurements", "gate", None),
    ("valid whitelisted share hit still warns but passes", "gate-wl", None),
]


def run():
    sv = _mod("schema/semantic_validate.py", "sv_adv")
    wg = _mod("extraction/wrapper_gate.py", "wg_adv")
    repo = sv.Repo(ROOT)
    fails, n_ok = [], 0
    tmp = Path(tempfile.mkdtemp(prefix="dr-adv-"))
    try:
        for m in MUTATIONS:
            if m["kind"] == "gate":
                mv = json.loads((ROOT / "extraction/measured-values.json").read_text())
                wl = json.loads((ROOT / "extraction/wrapper-whitelist.json").read_text())
                m["fn"](mv, wl)
                (tmp / "mv.json").write_text(json.dumps(mv))
                (tmp / "wl.json").write_text(json.dumps(wl))
                e, w, _ = wg.run(ROOT, tmp / "mv.json", tmp / "wl.json")
                pool = w if m["sev"] == "warn" else e
                ok = any(m["expect"] in x for x in pool) and (m["sev"] == "warn" and not e or m["sev"] == "error")
                got = f"errors={e[:2]} warnings={w[:2]}"
            else:
                r = repo
                if m["kind"] == "repo":
                    rr = tmp / f"repo{len(fails)}{n_ok}"
                    shutil.copytree(ROOT, rr, ignore=shutil.ignore_patterns("__pycache__"))
                    m["fn"](rr)
                    r = sv.Repo(rr)
                    spec = _ex(m["base"])
                else:
                    spec = _ex(m["base"])
                    m["fn"](spec)
                rep = sv.validate(spec, r, with_schema=m["schema"])
                ok = m["expect"] in rep.codes("error")
                got = sorted(rep.codes("error"))
            print(f"{'REJECTED' if ok else 'MISSED  '}  {m['name']:48} expect {m['expect']:28} got {got}")
            if ok:
                n_ok += 1
            else:
                fails.append(m["name"])
        c_ok = 0
        for name, base, fn in CONTROLS:
            if base == "gate":
                e, w, _ = wg.run(ROOT)
                ok, got = not e and not w, f"errors={e} warnings={w}"
            elif base == "gate-wl":
                mv = json.loads((ROOT / "extraction/measured-values.json").read_text())
                _h(mv, "features.pinned-workflow", 30000)
                wl = {"entries": [{"route": "/", "section": "features.pinned-workflow", "kind": "share", "reviewedBy": "build agent (agent attestation, not a human sign-off)",
                                   "justification": "Pinned workflow is one semantic walkthrough unit (test fixture).", "maxHeightPx": 40000}]}
                (tmp / "mv.json").write_text(json.dumps(mv))
                (tmp / "wl.json").write_text(json.dumps(wl))
                e, w, _ = wg.run(ROOT, tmp / "mv.json", tmp / "wl.json")
                ok, got = not e and any("whitelisted" in x for x in w), f"errors={e} warnings={len(w)}"
            else:
                spec = _ex(base)
                fn(spec)
                rep = sv.validate(spec, repo)
                ok = not rep.errors and not [i for i in rep.items if i[0] == "warn"]
                got = [(i[1], i[2]) for i in rep.items][:4]
            print(f"{'PASS    ' if ok else 'FAIL    '}  control: {name} {'' if ok else got}")
            c_ok += ok
            if not ok:
                fails.append("control: " + name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nadversarial: {n_ok}/{len(MUTATIONS)} mutations rejected, {c_ok}/{len(CONTROLS)} controls pass")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())
