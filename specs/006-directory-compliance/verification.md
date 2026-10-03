# Verification — local candidate 0.9.8

Date: 2026-10-03. This report records the local pre-integration validation snapshot.
The owner subsequently authorized commit, push and release; PR approval and CI still apply.
Portal upload and resubmission are outside that release step.

## Fresh results

- New metadata regression tests failed before implementation: three tests, nine failing subcases.
  The old packager accepted missing/unsafe support links, oversized listing text, duplicate
  starter prompts and an oversized translation subtitle.
- `python3 -m unittest discover -s tests -v`: 40 tests, 15.712 seconds, OK;
  pre-commit recheck after release documentation updates: 40 tests, 12.915 seconds, OK.
- `python3 scripts/validate-package.py`: version 0.9.8 valid, 55 patterns.
- `python3 scripts/package-plugin.py --check`: metadata valid for Codex and Claude Code.
- `python3 scripts/package-plugin.py`: all three archives built and validated.
- `claude plugin validate .`: passed.
- `claude plugin validate .claude-plugin/plugin.json --strict`: passed.
- `npx --yes skills@1.5.20 add . --list`: exactly one skill discovered, vietnamizer.
- `git diff --check`: no whitespace errors.
- Optional skill-creator `quick_validate.py`: initially blocked by missing PyYAML; resolved by
  running in a uv-managed isolated environment with PyYAML 6.0.2 and `/usr/bin/python3`.
  Command: `UV_HTTP_RETRIES=0 UV_HTTP_TIMEOUT=15 uv --native-tls run --no-project --python /usr/bin/python3 --with PyYAML==6.0.2 python /Users/fioenix/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/fioenix/Projects/vietnamizer`.
  Result: `Skill is valid!`, exit 0. uv emitted warnings for the deprecated `--native-tls` flag
  and the redundant `--no-project` flag; neither affected validation. No repository dependency,
  lock file or system Python package was added. The initial connection retry was interrupted.
- Inspected generated plugin ZIP: version 0.9.8, exactly one SKILL.md, canonical byte parity,
  English base subtitle, supportURL and vi-VN translations present; CRC check returned no error.

## Artifact digests

| Local candidate | SHA-256 |
|---|---|
| dist/vietnamizer.skill | b79ea5414be0f230abd1a7b074d66992bdbac02709a4ff2b1962f0884c7bbb60 |
| dist/vietnamizer-claude-org.zip | a9e5e1ccbaebf3e8edeb83971a3edd962ad8c359fad359d31b51128556503000 |
| dist/vietnamizer-plugin.zip | 3a26a3f4fe882941ed4f9e74d3e370462838f0cc50e614bff3102589efddb8ac |

Previous local 0.9.7 artifacts were copied to output/release-v0.9.7-assets before rebuilding dist.
The preserved plugin ZIP digest remains
125f3361b6c2a66d532dbf25b54619de3529a1f50979add88169760e984abb2d.
Published 0.9.7 release assets were not modified.

## Instruction review, not model-evaluation claims

The core now places a restricted-data boundary before editing, asks for user-redacted or synthetic
input, and forbids quoting, persisting or externally sending the restricted input. The feedback
branch now requires an explicit maintenance task and file authorization before calibration writes.
Public health prose and fictional examples remain eligible for ordinary editing.

These conclusions follow from source review. No new independent model run or native invocation
was executed to prove compliance behavior. Packaging tests do not prove policy adherence in every
run. The owner's earlier waived native/Claude/fallback tests were not reopened or recorded as passed.

## Remaining publication gates

Integrate this patch through the repository's PR/CI process and publish the updated privacy page.
The privacy URL currently points to remote main, not these uncommitted local changes.
Then use the matching new ZIP for portal review. Publisher verification, category confirmation,
security/privacy scans and skills-only eligibility still require direct portal evidence.
No claim is made that English listing text alone resolves the reported category finding.

## Independent review correction

Independent review of 6bda79c found that `translations or {}` allowed invalid falsey values
to pass the release gate. The manifest itself remained valid, but acceptance criterion 4 was
not fully met. A fresh subprocess regression test failed for [], false, 0 and an empty string.
The correction normalizes only omission/null; other non-map values are rejected. Positive
controls retain support for omission, null and an empty locale map.

Fresh full-suite result after the correction: 42 tests, 12.709 seconds, OK. Package and
distribution metadata validation both passed; `git diff --check` reported no whitespace errors.

The reviewer also noted malformed URL ports as a nonblocking robustness issue; the current
GitHub support URL is valid. That separate minor issue is not changed in this correction.
