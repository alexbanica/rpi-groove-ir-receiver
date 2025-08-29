#!/usr/bin/python
# -*- coding:utf-8 -*-

import argparse
import time
import sys
import IRReceiver

try:
    import pigpio
except Exception as e:
    print("Error importing pigpio. Make sure 'pigpio' Python package is installed.")
    print("Install: pip3 install pigpio")
    print("Also start the daemon: sudo pigpiod")
    raise

def main():
    parser = argparse.ArgumentParser(description="Record IR signals (raw pulses).")
    parser.add_argument("--in-gpio", type=int, default=17, help="GPIO pin number for IR receiver (BCM)")
    parser.add_argument("--out-file", type=str, required=True, help="Output JSON file to save the raw pulses")
    parser.add_argument("--timeout", type=float, default=10.0, help="Max seconds to wait for a signal")
    parser.add_argument("--gap", type=float, default=0.15, help="Gap in seconds to consider burst finished")
    parser.add_argument("--bursts", type=int, default=1, help="Number of bursts to capture (choose one)")

    args = parser.parse_args()

    pi = pigpio.pi()
    if not pi.connected:
        print("Could not connect to pigpio daemon. Start it with: sudo pigpiod")
        sys.exit(2)

    receiver = IRReceiver(pi, args.in_gpio)
    print(f"Waiting for IR signal on GPIO {args.in_gpio} (timeout {args.timeout}s). Press a button on the remote.")
    captured = []
    bursts_to_capture = max(1, args.bursts)
    for b in range(bursts_to_capture):
        print(f"Capture #{b+1}/{bursts_to_capture} ...")
        pulses = receiver.record_single(timeout=args.timeout, gap=args.gap)
        if not pulses:
            print("No signal captured (timeout).")
        else:
            print(f"Captured {len(pulses)} durations (first: {pulses[:8]})")
            captured.append(pulses)
        # small pause between captures
        time.sleep(0.2)

    if not captured:
        print("No bursts captured; exiting.")
        pi.stop()
        sys.exit(1)

    chosen = 0
    if len(captured) > 1:
        print(f"{len(captured)} bursts captured. Choose one to save (0-{len(captured)-1}):")
        for i, p in enumerate(captured):
            print(f"[{i}] durations={len(p)} first8={p[:8]}")
        try:
            s = input(f"Choose index (default 0): ").strip()
            if s != "":
                chosen = int(s)
                if chosen < 0 or chosen >= len(captured):
                    chosen = 0
        except Exception:
            chosen = 0

    pulses = IRReceiver.normalize_pulses(captured[chosen])
    IRReceiver.save_pulses(args.out_file, args.in_gpio, pulses)
    pi.stop()
    print("Done.")


if __name__ == "__main__":
    main()