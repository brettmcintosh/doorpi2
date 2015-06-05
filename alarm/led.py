import serial

from alarm import settings


class LEDRing(object):

    def __init__(self):
        self.device_path = settings.LED_DEVICE_PATH
        self.baudrate = settings.LED_DEVICE_BAUDRATE
        self.serial_connection = None

    def __enter__(self):
        self.serial_connection = serial.Serial(self.device_path, self.baudrate)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.serial_connection.close()

    def send_command(self, command):
        self.serial_connection.write(bytes(command, 'ascii'))
