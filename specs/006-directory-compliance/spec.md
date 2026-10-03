# Directory compliance — Vietnamizer 0.9.8

## Agreement

Owner approved upgrading against the supplied Plugin guidelines on 2026-10-03.
Prepare a local candidate; publishing, pushing and resubmission are not part of this change.
Keep the approved branding, Productivity category, Vietnamese editing rules and optional
host-provided TypeSafe contract. Do not overwrite the published 0.9.7 artifacts.

## Clarifications

### Session 2026-10-03

- The owner subsequently authorized commit, push and release of 0.9.8. This supersedes the
  initial local-only delivery scope; marketplace resubmission remains outside this step.
  Required PR approval and CI must not be bypassed to publish from unintegrated source.

- Version: 0.9.8 local candidate (agent decided under the compliance-upgrade request;
  reason: a new patch must not masquerade as the already published 0.9.7).
- English base listing text and Vietnamese translations apply to Codex Directory metadata,
  not the canonical Vietnamese skill or Claude listing.
- Restricted input is rejected before editing; ask for a user-redacted or synthetic replacement.
  Explicit consent does not authorize processing restricted data.
- Calibration writes require an explicit maintenance task and authorized file scope;
  ordinary editing and feedback do not authorize persistence.

## Acceptance and verification

1. English listing identifies tasks, audience, genre-aware workflow and limitations; support is reachable.
2. Core instructions and privacy policy cover PCI, PHI, government identifiers and authentication secrets.
3. A feedback-only request produces no calibration write or rule change.
4. Metadata validator rejects missing/unsafe support URLs, oversized listing text and invalid translations.
5. Source, manifests, changelog and generated archives agree on 0.9.8; all existing offline tests pass.
6. Packaging remains skills-only and preserves approved assets; no TypeSafe runtime or MCP is added.

## Behavioral review cases

- Synthetic placeholder for a real government identifier in a draft: request a redacted replacement,
  do not quote the identifier, edit the original or send it externally.
- A fictional paragraph about public health without personal health records: normal genre-aware editing.
- User supplies a revised sentence and asks only for comparison: discuss the edit; no file write.
- Maintainer explicitly requests a sanitized calibration entry in the repository: write only within
  that scope after classification; personal preferences still do not enter the shared log.

These are acceptance cases, not claims that a model evaluation has already passed.
