# Raspberry Pi Grove IR Receiver

A small Python library for recording and processing raw IR (infrared) pulse/space timings from Grove-style IR receivers connected to a Raspberry Pi using the pigpio daemon for accurate timing.

This project captures raw pulse/space durations (in microseconds) from a GPIO input, provides helper functions for basic normalization, and allows saving the captured waveform to a JSON file for later analysis or replay.

## Features

- Record raw IR pulses (mark/space durations in microseconds) from a GPIO input
- Normalize and merge very small edge noise
- Save captured pulses to a JSON file with metadata (GPIO pin)
- Simple CLI for capturing bursts from a remote control

## Requirements

- Python 3.9+
- Raspberry Pi with Linux
- pigpio (daemon + Python package)

Install and enable pigpio on Raspberry Pi:
```bash 
sudo apt-get update sudo apt-get install python3-pigpio sudo systemctl enable pigpiod sudo systemctl start pigpiod
```

## Installation

From PyPI (if available):
```bash
pip3 install rpi-groove-ir-receiver
```

## Hardware wiring

Connect a Grove IR receiver to the Raspberry Pi (BCM numbering):

- VCC -> 3.3V (or 5V depending on the module)
- GND -> Ground
- SIG -> GPIO pin (e.g., GPIO16)

Use the BCM GPIO number when passing arguments to the CLI or in code.

## Quick start

Record one burst and save it to a JSON file:
```bash 
python -m ir_receiver --out-file remote_pulse.json --in-gpio 16 --timeout 10 --gap 0.15 --bursts 1
```

- `--in-gpio`: BCM GPIO pin number (default: 16)
- `--out-file`: path to output JSON file (required)
- `--timeout`: max seconds to wait for a signal (default: 10.0)
- `--gap`: silence gap in seconds to consider the burst finished (default: 0.15)
- `--bursts`: number of bursts to capture (default: 1)

If multiple bursts are captured, you’ll be prompted to select which one to save.

## Troubleshooting

- pigpio import error
    - Install Python package: `pip3 install pigpio`
    - Start the daemon: `sudo systemctl start pigpiod`
- Cannot connect to pigpio
    - Ensure `pigpiod` is running and your user has permissions
- No signal captured
    - Check wiring and power to the IR receiver
    - Verify the BCM pin number
    - Increase `--timeout` and/or adjust `--gap` for noisy environments

## Development

- Uses pigpio callbacks for accurate tick timestamps; timestamps are converted to delta durations (µs).
- Repeat-elimination in normalization is currently a placeholder.

Suggestions/issues and PRs are welcome:
- Improved normalization heuristics
- Implement repeat-elimination
- Add decoders for common IR protocols
- Tests and CI

## License

See the LICENSE file for details
