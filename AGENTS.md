# AGENTS

## Project implementation status

The codebase is aligned to a DDD + Onion style layout.

### Layers

- `domains`: entities, DTOs, and interfaces.
- `applications`: business services and orchestration.
- `infrastructures`: pigpio and filesystem adapters.
- `controllers`: CLI request/response and coordination.
- `shared/constants`: centralized static strings and numeric thresholds.

Dependencies point inward. `controllers` and `infrastructures` may depend on application/domain contracts, while `domains` must stay independent of CLI parsing, filesystem persistence, pigpio, GPIO, and process-runtime concerns.

### Project-specific architecture

- `ir_receiver/domains/entities`: raw pulse, normalized pulse, and burst model objects.
- `ir_receiver/domains/dtos`: datastore-free transfer objects for captured output.
- `ir_receiver/domains/interfaces`: domain-facing contracts; every interface must use the `Interface` suffix.
- `ir_receiver/applications/services`: capture, burst selection, normalization, and persistence orchestration.
- `ir_receiver/infrastructures/gpio`: pigpio/GPIO boundary implementations.
- `ir_receiver/infrastructures/recorders`: concrete pulse capture adapters.
- `ir_receiver/infrastructures/persistences`: JSON pulse file writing adapters.
- `ir_receiver/controllers/requests` and `ir_receiver/controllers/responses`: CLI DTOs.
- `ir_receiver/shared/constants`: default GPIO, gap, timeout, burst, and threshold values.

### Naming standards

- Interfaces are suffixed with `Interface`.
- Abstract classes are prefixed with `Abstract`.
- Implementations of abstract classes remove the `Abstract` prefix and keep the remaining name.
- Service implementations match interface names without suffix.

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
