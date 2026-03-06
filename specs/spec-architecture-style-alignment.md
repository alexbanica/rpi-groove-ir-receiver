# Spec: Architecture and Coding Style Alignment + Requirements File

## Metadata
- Spec ID: `SPEC-2026-03-06-ARCH-ALIGNMENT`
- Branch: `spec/architecture-style-alignment`
- Status: `Approved`
- Authoring Date: `2026-03-06`

## 1. Purpose
Realign the current project to the architecture and coding-style guidelines defined in `AGENTS.md`, while preserving current runtime behavior and adding a platform-specific `requirements.txt`.

## 2. Definitions
- Entity: persisted domain object.
- DTO: non-persisted transfer object.
- Invariant: behavior that must remain unchanged after refactor.
- Platform-specific dependencies: dependencies selected by runtime/platform context (Raspberry Pi, Hobot, Jetson).

## 3. Scope
### In Scope
- Full structural refactor to DDD + Onion Architecture.
- Separation of domain and infrastructure responsibilities.
- Interface-first contracts and concrete implementations.
- Naming/style alignment from `AGENTS.md`:
  - packages named in plural form.
  - one class per file.
  - interfaces suffixed with `Interface`.
  - implementations matching interface name without `Interface`.
- Centralization of static strings/constants.
- Add `requirements.txt` including platform-specific dependencies.
- Fix packaging/configuration issues in current project setup.
- Update `README.md` and `AGENTS.md` to reflect resulting architecture and installation flow.
- Add/adjust tests for all business logic and regression safety.

### Out of Scope
- New decoding protocols or feature additions unrelated to architecture/style alignment.
- Behavioral redesign of IR capture workflow.

## 4. Mandatory Invariants (Behavior Must Not Change)
1. CLI arguments and defaults remain exactly:
   - `--in-gpio` default `16`
   - `--out-file` required
   - `--timeout` default `10.0`
   - `--gap` default `0.15`
   - `--bursts` default `1`
2. Output JSON shape remains exactly:
   - `{ "gpio_in": <int>, "pulse_us": <list[int]> }`
3. Current normalization behavior remains functionally equivalent, including:
   - tiny-duration merge threshold logic.
   - trailing long-gap cleanup behavior.
   - repeat-removal path remains placeholder/no-op unless separately specified.

## 5. Architecture Specification
The implementation must produce and enforce onion-style dependency direction:
- `domains` layer: pure business rules/entities/value objects/interfaces.
- `applications` layer: use cases/services orchestrating domain operations.
- `infrastructures` layer: pigpio adapters, file persistence, and external integrations.
- `controllers` layer: CLI request/response orchestration and argument parsing.

Dependency rule:
- Outer layers may depend inward.
- Domain layer must not depend on infrastructure or framework-specific code.

## 6. API/Integration Documentation Rule
- No HTTP API exists in this project; therefore OpenAPI and `/http/*.http` artifacts are explicitly **not applicable** for this spec.

## 7. Requirements File Specification
Create `requirements.txt` with platform-specific dependency policy.
- Must include `pigpio`.
- Must include platform-conditional dependencies currently represented in packaging logic (`RPi.GPIO`, `spidev`, `Hobot.GPIO`, `Jetson.GPIO`) with deterministic install guidance.
- README must document installation paths clearly (including platform notes).

## 8. Build, Quality, and Regression Requirements
1. Project builds successfully.
2. No compilation/runtime warnings introduced by refactor.
3. Tests added/updated for all business logic.
4. All tests pass.
5. Regression analysis documented in PR/commit notes.
6. If a behavior regression is discovered, implementation must stop and request clarification.

## 9. Deliverables
- Refactored codebase aligned to architecture/style rules.
- `requirements.txt` created and documented.
- Updated packaging/setup configuration.
- Updated `README.md` and `AGENTS.md`.
- Passing tests for business logic.

## 10. Acceptance Criteria
- All mandatory invariants in section 4 are satisfied.
- All in-scope items are implemented.
- Lint/build/tests pass.
- Documentation updates are complete and accurate.

## 11. Assumptions
- Runtime target remains Linux-based SBC devices where pigpio usage is valid.
- Existing CLI remains the primary external interface.
- No additional external API contracts are required.
