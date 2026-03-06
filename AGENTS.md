# AGENTS

## Project implementation status

The codebase is aligned to a DDD + Onion style layout.

### Layers

- `domains`: entities, DTOs, and interfaces.
- `applications`: business services and orchestration.
- `infrastructures`: pigpio and filesystem adapters.
- `controllers`: CLI request/response and coordination.
- `shared/constants`: centralized static strings and numeric thresholds.

### Invariants

The following behavior must remain stable unless a new approved spec changes it:

1. CLI flags and defaults:
   - `--in-gpio=16`
   - `--out-file` required
   - `--timeout=10.0`
   - `--gap=0.15`
   - `--bursts=1`
2. JSON output shape:
   - `{ "gpio_in": <int>, "pulse_us": <list[int]> }`
3. Pulse normalization behavior and repeat-removal placeholder semantics.

### Testing

- Unit tests live in `tests/`.
- Run with:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

### API docs scope

No HTTP API exists. OpenAPI and `.http` artifacts are not applicable for the current project scope.
