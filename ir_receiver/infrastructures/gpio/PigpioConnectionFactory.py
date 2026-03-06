from ir_receiver.shared.constants.CliStrings import CliStrings


class PigpioConnectionFactory:
    def create_connection(self):
        try:
            import pigpio
        except Exception:
            print(CliStrings.PIGPIO_IMPORT_ERROR)
            print(CliStrings.PIGPIO_INSTALL_HINT)
            print(CliStrings.PIGPIO_DAEMON_HINT)
            raise

        return pigpio.pi()
