import RPi.GPIO as io
import time
import threading
import logging

import settings
import camera


class Sensor(object):
    """A single sensor."""

    def __init__(self, pin=None, mode=io.BCM, name='', pull_up=False):
        self.pin = pin
        self.mode = mode
        self.name = name
        self.pull_up = pull_up

    def setup(self):
        io.setmode(self.mode)

        if self.pull_up:
            io.setup(self.pin, io.IN, pull_up_down=io.PUD_UP)
        else:
            io.setup(self.pin, io.IN)

    def read(self):
        if io.input(self.pin):
            return True
        return False


class Scanner(object):
    """An array of sensors that feeds data into the remote Alarm object."""

    def __init__(self):
        self.sensors = {}
        self.scan_thread = None
        self.stop_scan = False
        # self._scan_was_stopped = multiprocessing.Event()
        self.alarm = None
        self.camera = None
        self.setup()

    def setup(self):
        """Setup all sensors in settings file, then connect to remote alarm and camera objects."""
        for sensor in settings.SENSORS:
            s = Sensor(**sensor)
            s.setup()
            self.sensors[s.name] = s
            logging.debug('Initialized %s sensor.', s.name)

    def scan(self):
        """Read each sensor indefinitely at the specified refresh rate.  Send results to alarm and record with camera."""
        # reset stop event
        # self._scan_was_stopped.clear()

        # scan all sensors until stop is called
        while not self.stop_scan:
            for sensor in self.sensors.values():
                # send message to alarm and record if sensor senses something
                if sensor.read() and self.camera:
                    self.camera.activate()
                    logging.debug('%s sensor activated.')
                    if self.alarm:
                        self.notify_alarm(sensor.name)

            time.sleep(settings.SENSOR_REFRESH_RATE)
        logging.debug('Exiting scan thread.')

    def notify_alarm(self, sensor_name):
        """Send sensor data to remote alarm and camera objects."""
        self.alarm.receive_sensor_message(sensor_name)
        logging.debug('Notifying alarm that %s sensor was activated.', sensor_name)

    def start(self):
        """Start a scan thread."""
        if not self.scan_thread:
            # start camera
            self.camera = camera.Camera()
            self.camera.scanner = self
            self.scan_thread = threading.Thread(target=self.scan, name='ScanThread')
            self.scan_thread.daemon = True
            self.scan_thread.start()
            logging.debug('Scanner started.')

    def stop(self):
        """Stop the scan loop in the scan thread."""
        self.stop_scan = True
        logging.debug('Waiting for scan thread to stop.')
        logging.debug(threading.enumerate())
        if self.camera:
            self.camera.close()
            self.camera = None
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
            logging.debug('Scan thread stopped.')
            logging.debug(threading.enumerate())
        self.stop_scan = False
        self.scan_thread = None

    def shutdown(self):
        self.sensors = {}
        io.cleanup()