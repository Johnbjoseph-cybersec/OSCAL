# Constraint test instances

Small OSCAL instances that exercise Metaschema constraints defined in `src/metaschema`.
Files named `valid-*` must validate with no constraint findings. Files named `invalid-*` must fail
with exactly the constraint ids listed for them in `expected.json`.

The current set covers the reference constraints added for usnistgov/OSCAL#2296:

- `assessment-results/`: a finding or risk must reference an observation that exists, a finding must
  reference a risk that exists, observation and risk UUIDs must be unique, and a risk log entry must
  reference a response defined in the same risk. The risk log check is defined on the shared `risk`
  assembly, so it also applies to risks in a POA&M.

Five of the `invalid-*` cases (missing observation or risk, duplicate observation or risk UUID) test the
`assessment-results` root constraints proposed in usnistgov/OSCAL#2298. Without those constraints they
report no findings, so run them on a branch that includes both.

## Running

The runner validates each instance against the module in this branch, not the module compiled into
the CLI. It needs Python 3 and either `oscal-cli` (preferred, because it provides OSCAL-specific
Metapath functions such as `has-oscal-namespace`) or `metaschema-cli`, both from the
metaschema-framework project.

```sh
python3 run_constraint_tests.py /path/to/oscal-cli metaschema
```

The exit code is non-zero if any instance reports a different set of constraint ids than expected.
