import time
import threading
import logging
from datetime import datetime

import settings
import sensor
import routines
import notifications
from models import authenticate_nfc


ALARM_CODES = (settings.ARMED, settings.DISARMED)
ARMED = settings.ARMED
DISARMED = settings.DISARMED


class Alarm(object):

    def __init__(self):
        self.process_lock = threading.Lock()
        self._status = None
        self._update_status_from_file()
        self.is_triggered = False
        self.entry_time = None
        self.scanner = sensor.Scanner()
        self.scanner.alarm = self
        self.current_routine = None
        self.setup()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        assert status in ALARM_CODES
        # save status to STATUS_PATH file
        with open(settings.STATUS_FILE_PATH, 'w') as f:
            f.write(status)
        self._status = status
        logging.debug('Alarm status changed to %s.', status)

    def _update_status_from_file(self):
        with open(settings.STATUS_FILE_PATH, 'r') as f:
            status = f.read().strip()
        if status not in ALARM_CODES:
            raise SettingsError('Invalid status in STATUS_FILE_PATH file or ARMED/DISARMED settings misconfigured.')
        self._status = status

    def get_status(self):
        return self.status, self.is_triggered, self.entry_time

    def setup(self):
        # if previously armed, start the sensor scan
        if self.status == settings.ARMED:
            logging.info('Alarm was shutdown while armed.  Rearming.')
            try:
                self.scanner.start()
            except:
                logging.critical('Camera error.')

    def arm(self):
        """Run the arm routine and start the arm countdown in a separate thread."""
        if self.status == settings.DISARMED:
            self.status = settings.ARMED
            self.start_routine(routines.ArmRoutine())
            arm_thread = threading.Thread(target=self._arm_countdown, name='Countdown Thread')
            arm_thread.start()
            logging.info('Starting arm countdown.')

    def _arm_countdown(self):
        time.sleep(settings.COUNTDOWN_DURATION + 1)
        if not self.current_routine.canceled and isinstance(self.current_routine, routines.ArmRoutine):
            self.current_routine = None
            # start scanner
            self.scanner.start()
            logging.info('System Armed.')
        else:
            logging.info('Arming canceled.')

    def disarm(self):
        if self.status == settings.ARMED:
            self.start_routine(routines.DisarmRoutine())
            self.status = settings.DISARMED
            self.is_triggered = False
            self.entry_time = None
            self.scanner.stop()
            logging.info('System Disarmed.')

    def quickarm(self):
        if self.status == settings.DISARMED:
            self.status = settings.ARMED
            self.scanner.start()
            logging.info('System Armed (quickarm).')

    def quickdisarm(self):
        if self.current_routine:
            self.current_routine.cancel()
        if self.status == settings.ARMED:
            self.status = settings.DISARMED
            self.scanner.stop()
            self.is_triggered = False
            self.entry_time = None
            logging.info('System Disarmed (quickdisarm).')

    def trigger(self, sensor_name):
        """
        This is called the first time any sensor senses something.
        """
        self.is_triggered = True
        self.entry_time = datetime.now().strftime('%I:%M%p')
        msg = notifications.create_email_message(sensor_name)
        self.start_routine(routines.EntryRoutine(msg))
        logging.info('Alarm triggered.  Sensor: %s.', sensor_name)

    def receive_sensor_message(self, sensor_name):
        logging.debug("Sensor message received.  Sensor: %s.", sensor_name)
        with self.process_lock:
            if self.status == settings.ARMED:
                if not self.is_triggered:
                    self.trigger(sensor_name)

    def receive_nfc_message(self, nfc_id):
        if authenticate_nfc(str(nfc_id)):
            with self.process_lock:
                logging.info('Received valid NFC key. %s', nfc_id)
                if self.status == settings.ARMED:
                    self.disarm()
                elif self.status == settings.DISARMED:
                    self.arm()
        else:
            logging.info('Received invalid NFC key.  Key: %s.', nfc_id)

    def start_routine(self, routine):
        # cancel any running routines
        if self.current_routine:
            self.current_routine.cancel()
            logging.debug('Canceling %s routine.', self.current_routine)

        self.current_routine = routine
        self.current_routine.start()
        logging.debug('Starting %s routine.', self.current_routine)


class SettingsError(Exception):
    pass
