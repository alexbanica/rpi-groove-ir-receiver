import time

from ir_receiver.domains.interfaces.PulseRecorderInterface import PulseRecorderInterface


class PigpioPulseRecorder(PulseRecorderInterface):
    def __init__(self, pigpio_connection, gpio_in: int):
        self._pigpio_connection = pigpio_connection
        self._gpio_in = gpio_in
        self._callback = None

    def record_single(self, timeout: float, gap: float) -> list[int]:
        pigpio_module = self._import_pigpio()
        self._pigpio_connection.set_mode(self._gpio_in, pigpio_module.INPUT)
        self._pigpio_connection.set_pull_up_down(self._gpio_in, pigpio_module.PUD_OFF)

        recording: list[int] = []
        active = {
            "recording": False,
            "last_tick": None,
            "last_activity_time": time.time(),
        }

        def callback(_gpio: int, level: int, tick: int):
            if level == 2:
                return

            if active["last_tick"] is None:
                active["last_tick"] = tick
                active["recording"] = True
                return

            delta = (tick - active["last_tick"]) & 0xFFFFFFFF
            recording.append(delta)
            active["last_tick"] = tick
            active["last_activity_time"] = time.time()

        self._callback = self._pigpio_connection.callback(self._gpio_in, pigpio_module.EITHER_EDGE, callback)

        start_time = time.time()
        active["last_activity_time"] = start_time

        try:
            while True:
                now = time.time()
                if not active["recording"]:
                    if now - start_time > timeout:
                        break
                    time.sleep(0.01)
                    continue

                if now - active["last_activity_time"] > gap:
                    break

                if now - start_time > timeout:
                    break

                time.sleep(0.01)
        finally:
            if self._callback is not None:
                self._callback.cancel()
                self._callback = None

        return recording

    def _import_pigpio(self):
        import pigpio

        return pigpio
