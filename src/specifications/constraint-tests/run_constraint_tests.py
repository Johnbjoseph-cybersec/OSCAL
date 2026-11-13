#!/usr/bin/env python3
"""Run the constraint test instances in this directory against the OSCAL metaschema modules.

Usage:
  python3 run_constraint_tests.py /path/to/oscal-cli metaschema
  python3 run_constraint_tests.py /path/to/metaschema-cli

Each instance listed in expected.json is validated with `validate-content` against the matching
module in src/metaschema, so the result reflects the constraints in this branch rather than the
ones compiled into the CLI. Prefer `oscal-cli metaschema`, which also provides OSCAL-specific
Metapath functions such as `has-oscal-namespace`. A test passes when the set of constraint ids
reported in the SARIF output equals the expected set (an empty set means the instance must be valid).
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
METASCHEMA_DIR = HERE.parents[1] / "metaschema"
MODULES = {
    "assessment-results": "oscal_assessment-results_metaschema.xml",
    "plan-of-action-and-milestones": "oscal_poam_metaschema.xml",
}


def reported_rule_ids(cli_prefix, module, instance):
    with tempfile.TemporaryDirectory() as tmp:
        sarif_path = pathlib.Path(tmp) / "out.sarif"
        subprocess.run(
            [*cli_prefix, "validate-content", "--no-color", "-q", "-m", str(module), "-o", str(sarif_path), str(instance)],
            capture_output=True, text=True, check=False,
        )
        if not sarif_path.exists():
            raise RuntimeError(f"no SARIF output for {instance}")
        sarif = json.loads(sarif_path.read_text())
    ids = set()
    for run in sarif.get("runs", []):
        rules = run.get("tool", {}).get("driver", {}).get("rules", [])
        for res in run.get("results", []):
            if res.get("kind", "fail") != "fail":
                continue
            rule_id = res.get("ruleId")
            if rule_id is None and "ruleIndex" in res:
                rule_id = rules[res["ruleIndex"]].get("id")
            ids.add(rule_id)
    return ids


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cli = sys.argv[1:]
    expected = json.loads((HERE / "expected.json").read_text())
    failures = 0
    for rel, want in expected.items():
        model = rel.split("/", 1)[0]
        got = reported_rule_ids(cli, METASCHEMA_DIR / MODULES[model], HERE / rel)
        ok = got == set(want)
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {rel}  expected={sorted(want)} reported={sorted(got)}")
    print(f"{len(expected) - failures} passed, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
