class CliStrings:
    DESCRIPTION = "Record IR signals (raw pulses)."
    ARG_IN_GPIO_HELP = "GPIO pin number for IR receiver (BCM)"
    ARG_OUT_FILE_HELP = "Output JSON file to save the raw pulses"
    ARG_TIMEOUT_HELP = "Max seconds to wait for a signal"
    ARG_GAP_HELP = "Gap in seconds to consider burst finished"
    ARG_BURSTS_HELP = "Number of bursts to capture (choose one)"

    PIGPIO_IMPORT_ERROR = "Error importing pigpio. Make sure 'pigpio' Python package is installed."
    PIGPIO_INSTALL_HINT = "Install: pip3 install pigpio"
    PIGPIO_DAEMON_HINT = "Also start the daemon: sudo pigpiod"
    PIGPIO_CONNECT_ERROR = "Could not connect to pigpio daemon. Start it with: sudo pigpiod"

    WAITING_FOR_SIGNAL = "Waiting for IR signal on GPIO {gpio} (timeout {timeout}s). Press a button on the remote."
    CAPTURE_PROGRESS = "Capture #{index}/{total} ..."
    NO_SIGNAL_CAPTURED = "No signal captured (timeout)."
    CAPTURED_DURATIONS = "Captured {count} durations (first: {first})"
    NO_BURSTS_CAPTURED = "No bursts captured; exiting."

    CHOOSE_PROMPT_HEADER = "{count} bursts captured. Choose one to save (0-{max_index}):"
    CHOOSE_ENTRY = "[{index}] durations={count} first8={first8}"
    CHOOSE_INDEX_PROMPT = "Choose index (default 0): "

    SAVED_FILE = "Saved {count} durations to {filename}"
    DONE = "Done."
