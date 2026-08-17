# SPEC: Emitter publish-credentials alignment

Status: Approved

## Purpose

Align this receiver's GitHub Actions Forgejo publishing credentials with the
post-release pattern adopted by `rpi-groove-ir-emitter`.

## Delivered behavior

- The tag-only publish step receives `FORGEJO_PACKAGE_USERNAME` and
  `FORGEJO_PACKAGE_TOKEN` from GitHub Actions secrets.
- The publisher requires both inputs before executing any release command.
- The publisher removes both source credential variables from every child
  process environment. Only the Twine upload child receives their mapped
  `TWINE_USERNAME` and `TWINE_PASSWORD` values.
- Workflow and publisher tests assert secret scoping, missing-username failure,
  and credential isolation.

## Scope and constraints

The existing tag rules, artifact validation, Forgejo endpoints, release flow,
and receiver runtime behavior remain unchanged. No hosted workflow or live
Forgejo publication is performed by this change.

## Validation performed

Recorded after implementation in the companion plan.

## Documentation changes

The maintainer release instructions now require both repository secrets and
describe their upload-only handling.
