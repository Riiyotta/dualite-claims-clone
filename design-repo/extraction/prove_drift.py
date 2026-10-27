#!/usr/bin/env python3
"""Prove that verify_all.py actually catches drift: copy the package to a scratch dir, inject one
defect per case, run verify_all there, and require it to FAIL with the expected message.
The untouched copy must PASS. Citation/source cases need the clone source tree (auto-detected
from measured-values.json sourceRoot, or --source-root / DESIGN_REPO_SOURCE_ROOT); without it
they are reported as SKIP, never as pass.

    python3 extraction/prove_drift.py [--source-root <clone project dir>]
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent


def src_root():
    a = sys.argv
    if "--source-root" in a:
        return Path(a[a.index("--source-root") + 1]).resolve()
    if os.environ.get("DESIGN_REPO_SOURCE_ROOT"):
        return Path(os.environ["DESIGN_REPO_SOURCE_ROOT"]).resolve()
    return (ROOT / json.loads((ROOT / "extraction/measured-values.json").read_text()).get("sourceRoot", "..")).resolve()


def jedit(rel, fn):
    def f(r):
        p = r / rel
        d = json.loads(p.read_text())
        fn(d)
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    return f


def tedit(rel, old, new):
    def f(r):
        p = r / rel
        t = p.read_text()
        assert old in t, f"drift fixture out of date: {old!r} not in {rel}"
        p.write_text(t.replace(old, new, 1))
    return f


CASES = [
    # (name, mutate, expected substring in verify_all output, needs source tree)
    ("phantom allowlist section", jedit("tokens/llm/component-allowlist.json", lambda d: d["sections"].update({"pricing.tiers": d["sections"]["faq.accordion"]})), "phantom sections", False),
    ("contract without allowlist entry", jedit("tokens/llm/component-allowlist.json", lambda d: d["sections"].pop("faq.accordion")), "missing from allowlist", False),
    ("allowlistVersion drift", jedit("registry.manifest.json", lambda d: d.update(allowlistVersion="9.9.9")), "allowlistVersion", False),
    ("manifest count drift", jedit("registry.manifest.json", lambda d: d["counts"].update(sections=99)), "manifest counts drift", False),
    ("README count drift", tedit("README.md", "| sections | 20 |", "| sections | 21 |"), "README counts block", False),
    ("registry availability loosened", jedit("assets/asset-roles.json", lambda d: d["roles"]["video.testimonial-source"].update(availability="generation-safe")), "registry generation-safe != pinned", False),
    ("pin removed from verify_all", tedit("extraction/verify_all.py", '    "logo.customer-source": "blocked-for-generation",\n', ""), "logo.customer-source has no pin", False),
    ("pin removed from validator only", tedit("schema/semantic_validate.py", '    "logo.customer-source": "blocked-for-generation",\n', ""), "verify_all PINNED_AVAILABILITY != semantic_validate", False),
    ("contract + allowlist flipped together (loader eligible)", lambda r: (jedit("sections/runtime.intro-loader.json", lambda d: d.update(retrievalEligible=True))(r),
                                                                      jedit("tokens/llm/component-allowlist.json", lambda d: d["sections"]["runtime.intro-loader"].update(retrievalEligible=True))(r)), "contract retrievalEligible True != pin False", False),
    ("runtime-looking section not pinned", jedit("sections/editorial.case-study.json", lambda d: d.update(title="Case study modal")), "looks like runtime UI", False),
    ("retrieval pin removed from verify_all", tedit("extraction/verify_all.py", '"runtime.intro-loader", "utility.scroll-progress"', '"utility.scroll-progress"'), "RETRIEVAL_INELIGIBLE != semantic_validate", False),
    ("schema edited by hand", jedit("schema/pagespec.schema.json", lambda d: d["definitions"]["content.faq.accordion"]["properties"].update(extra={"type": "string"})), "schema drifted", False),
    ("contract field added without schema regen", jedit("sections/faq.accordion.json", lambda d: d["content"].update(badge={"type": "text", "maxWords": 2})), "schema drifted", False),
    ("token catalog hand-edited", jedit("tokens/llm/token-catalog.json", lambda d: d["tokens"]["color.olive"].update(value="#000000")), "token-catalog.json drifted", False),
    ("foundation token edited, catalog stale", jedit("tokens/00-foundation/color.json", lambda d: d["tokens"]["color.olive"].update(value="#3D5A2B")), "token-catalog.json drifted", False),
    ("policy category not in catalog", jedit("tokens/llm/token-policy.json", lambda d: d["styleProperties"]["accent"].update(categories=["typography"])), "category typography not in catalog", False),
    ("graph rule without validator", jedit("compatibility/graph.json", lambda d: d["rules"].append({"id": "NO_TWO_VIDEOS", "severity": "warn", "rule": "x"})), "differ from validator GRAPH_RULE_IDS", False),
    ("graph severity flipped", jedit("compatibility/graph.json", lambda d: [r.update(severity="error") for r in d["rules"] if r["id"] == "AUTOPLAY_BUDGET"]), "AUTOPLAY_BUDGET: graph severity error", False),
    ("template references missing contract", jedit("templates/templates.json", lambda d: d["templates"]["template.home"]["nodes"].append({"section": "pricing.tiers", "region": "main", "required": False, "repeatable": False})), "has no contract", False),
    ("route mapped twice", jedit("templates/routes.json", lambda d: d["routes"].append(dict(d["routes"][0]))), "mapped 2x", False),
    ("motion pattern removed", jedit("tokens/00-foundation/motion-patterns.json", lambda d: d["patterns"].pop("accordion-height")), "unknown pattern accordion-height", False),
    ("loader timeline offset drift", jedit("tokens/00-foundation/motion-patterns.json", lambda d: d["patterns"]["intro-loader-seal"]["timeline"][5].update(t=2000)), "timeline offsets drifted from site.js", False),
    ("generated example leaks brand", jedit("schema/examples/home.generated.pagespec.json", lambda d: d["nodes"][1]["content"].update(brandLabel="Dualite Claims")), "home.generated.pagespec.json", False),
    ("wrapper measurement removed", jedit("extraction/measured-values.json", lambda d: d["sectionHeights"]["pages"]["/"]["live"]["sections"].pop("hero.claims-intro")), "missing measurement for hero.claims-intro", False),
    ("wrapper threshold loosened in code", tedit("extraction/wrapper_gate.py", "HERO_WARN_PX, HERO_ERROR_PX = 1800, 3000", "HERO_WARN_PX, HERO_ERROR_PX = 1800, 30000"), "thresholds drifted", False),
    ("entryPoint outside package", jedit("registry.manifest.json", lambda d: d["entryPoints"].update(spec="../CLONE_SPEC.md")), "outside package", False),
    ("absolute machine path", tedit("README.md", "# Dualite Claims", "# Dualite Claims (" + "/" + "Users/someone/x)"), "absolutePaths", False),
    ("junk file", lambda r: (r / ".DS_Store").write_text("x"), "junk=", False),
    ("out-of-range citation", jedit("sections/hero.claims-intro.json", lambda d: d["responsive"]["evidence"].update(cite="public/assets/css/site.css:9000")), "out of range", True),
    ("in-range but wrong-content citation", jedit("tokens/00-foundation/color.json", lambda d: d["tokens"]["color.olive"]["evidence"].update(cite="public/assets/css/site.css:24")), "does not contain", True),
    ("source tag/marker moved", jedit("sections/hero.claims-intro.json", lambda d: d["source"].update(marker='<section className={"hero-v2"}')), "tag/marker", True),
    ("token value not in source CSS", lambda r: (jedit("tokens/00-foundation/color.json", lambda d: d["tokens"]["color.lime"].update(value="#C5D69B"))(r), subprocess.run([sys.executable, "extraction/token_catalog.py", "--write"], cwd=r, capture_output=True)), "not in site.css", True),
]


def run_verify(r, src):
    args = [sys.executable, "extraction/verify_all.py"] + (["--source-root", str(src)] if src else ["--source-root", str(r / "__no_source__")])
    p = subprocess.run(args, cwd=r, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return p.returncode, p.stdout + p.stderr


def main():
    src = src_root()
    have = (src / "src").is_dir() and (src / "public").is_dir()
    base = Path(tempfile.mkdtemp(prefix="dr-drift-"))
    ok = fails = skips = 0
    control_ok = False
    try:
        ctrl = base / "control"
        shutil.copytree(ROOT, ctrl, ignore=shutil.ignore_patterns("__pycache__"))
        rc, out = run_verify(ctrl, src if have else None)
        control_ok = rc == 0
        print(f"{'PASS ' if rc == 0 else 'FAIL '} control: untouched copy passes verify_all (exit {rc})")
        if rc != 0:
            print(out)
            fails += 1
        for i, (name, fn, expect, needs_src) in enumerate(CASES):
            if needs_src and not have:
                print(f"SKIP  {name} (no clone source tree; citation checks degrade to WARN in a standalone copy)")
                skips += 1
                continue
            r = base / f"c{i}"
            shutil.copytree(ROOT, r, ignore=shutil.ignore_patterns("__pycache__"))
            fn(r)
            rc, out = run_verify(r, src if have else None)
            caught = rc != 0 and expect in out
            line = next((l for l in out.splitlines() if expect in l), "").strip()[:150]
            print(f"{'CAUGHT' if caught else 'MISSED'} {name:52} -> {line}")
            ok += caught
            fails += not caught
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"\nprove_drift: {ok}/{len(CASES) - skips} drift cases caught, {skips} skipped, control {'passes' if control_ok else 'FAILS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
