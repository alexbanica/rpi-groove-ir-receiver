# Raspberry Pi Grove IR Receiver

Python library and CLI for recording and processing raw IR pulse/space timings from Grove-style IR receivers connected to Linux SBCs through `pigpio`.

## Features

- Capture raw pulse durations in microseconds from a GPIO input.
- Normalize captured pulses with deterministic threshold logic.
- Save pulses to JSON for replay or analysis.
- Capture one or multiple bursts and select the burst to persist.
- Layered architecture aligned to DDD and Onion principles.

## Requirements

- Python 3.9+
- Linux SBC (Raspberry Pi, Hobot, or Jetson)
- `pigpiod` daemon running

Install dependencies:

```bash
pip install -r requirements.txt
```

Install and enable `pigpiod`:

```bash
sudo apt-get update
sudo apt-get install -y python3-pigpio pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## Platform-specific dependency policy

`requirements.txt` includes marker-based platform-specific packages:

- Raspberry Pi: `RPi.GPIO`, `spidev`
- Hobot: `Hobot.GPIO`
- Jetson: `Jetson.GPIO`
- Common: `pigpio`

## Project structure

```text
ir_receiver/
  applications/services/
  controllers/
    requests/
    responses/
  domains/
    dtos/
    entities/
    interfaces/
  infrastructures/
    gpio/
    persistences/
    recorders/
  shared/constants/
```

## CLI usage

Capture one burst and save to JSON:

```bash
python -m ir_receiver --out-file remote_pulse.json --in-gpio 16 --timeout 10 --gap 0.15 --bursts 1
```

Arguments and defaults:

- `--in-gpio` (default: `16`)
- `--out-file` (required)
- `--timeout` (default: `10.0`)
- `--gap` (default: `0.15`)
- `--bursts` (default: `1`)

Output JSON schema remains:

```json
{
  "gpio_in": 16,
  "pulse_us": [9000, 4500, 560]
}
```

## Development

Run tests:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Troubleshooting

- Cannot import `pigpio`:
  - `pip install pigpio`
- Cannot connect to daemon:
  - `sudo systemctl start pigpiod`
- No capture detected:
  - Validate wiring and BCM pin.
  - Increase `--timeout` or adjust `--gap`.

## License

See [LICENSE](LICENSE).
