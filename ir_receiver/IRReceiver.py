#!/usr/bin/env python3
# language: python

import json
import time
from typing import List

try:
    import pigpio
except Exception as e:
    print("Error importing pigpio. Make sure 'pigpio' Python package is installed.")
    print("Install: pip3 install pigpio")
    print("Also start the daemon: sudo pigpiod")
    raise


class IRReceiver:
    """
    Record raw IR pulses (pulse/space durations in microseconds) from a GPIO input.

    Usage:
      r = IRReceiver(pi, gpio_in)
      pulses = r.record_single(timeout=5.0, gap=0.15)
    """

    def __init__(self, pi: pigpio.pi, gpio_in: int, invert: bool = True):
        """
        invert: many IR receivers produce a 'low' (0) mark when IR is present.
                If True, this class will treat the active/mark as 1 internally.
        """
        self.pi = pi
        self.gpio = gpio_in
        self.invert = invert
        self._cb = None

    def _edge_callback(self, gpio, level, tick):
        # This will be patched at runtime; placeholder
        pass

    def record_single(self, timeout: float = 10.0, gap: float = 0.15) -> List[int]:
        """
        Record until a gap (no edges) of 'gap' seconds indicates the end of a burst.
        Returns a list of durations in microseconds: [mark, space, mark, space, ...]
        If nothing recorded within timeout seconds, returns empty list.
        """
        pi = self.pi
        gpio = self.gpio

        pi.set_mode(gpio, pigpio.INPUT)
        pi.set_pull_up_down(gpio, pigpio.PUD_OFF)

        # We'll track edges and durations manually
        recording = []
        last_tick = None
        last_level = None
        active = {"recording": False, "finished": False, "last_tick": None, "last_level": None}

        def cb(g, level, tick):
            # level: 0,1,2 (2 is watchdog timeout)
            if level == 2:
                # watchdog expiration - treat as gap (no edges)
                now = time.time()
                # handle gap in main loop
                return
            t_us = tick  # pigpio tick (microseconds modulo)
            if active["last_tick"] is None:
                # first edge
                active["last_tick"] = t_us
                active["last_level"] = level
                active["recording"] = True
                return
            # compute delta in microseconds handling wrap-around
            dt = (t_us - active["last_tick"]) & 0xFFFFFFFF
            # convert to signed? pigpio tick is unsigned wrap, this yields positive delta
            recording.append(dt)
            active["last_tick"] = t_us
            active["last_level"] = level
            # reset a watchdog timer by setting last activity time externally
            active["last_activity_time"] = time.time()

        # Attach callback
        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, cb)
        # Set a watchdog on the pin to generate an edge  (not necessary; we'll poll time)
        # We'll use a simple polling loop to detect gaps
        start_time = time.time()
        active["last_activity_time"] = start_time

        try:
            while True:
                now = time.time()
                if not active["recording"]:
                    # wait for first edge until timeout
                    if now - start_time > timeout:
                        # timed out without seeing anything
                        break
                    time.sleep(0.01)
                    continue
                # If recording and no activity for 'gap', finish
                if now - active["last_activity_time"] > gap:
                    # End of burst
                    break
                # safety timeout
                if now - start_time > timeout:
                    break
                time.sleep(0.01)
        finally:
            # release callback
            if self._cb is not None:
                self._cb.cancel()
                self._cb = None

        return recording

    @staticmethod
    def normalize_pulses(pulses: List[int]) -> List[int]:
        """
        pigpio callback records durations between edges. We want a list of durations
        that start with a mark (carrier ON) duration. Depending on receiver polarity
        and when edges start, the list may need no change or may need to be shifted.
        This function just ensures integers and returns a copy; protocol-specific
        normalization (like merging tiny gaps) can be added if needed.
        """
        return [int(p) for p in pulses]


def save_pulses(filename: str, gpio_in: int, pulses: List[int]):
    data = {"gpio_in": int(gpio_in), "pulse_us": [int(p) for p in pulses]}
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(pulses)} durations to {filename}")
