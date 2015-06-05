from datetime import datetime
import threading
import time
import logging
try:
    from picamera.camera import PiCamera
except (RuntimeError, AttributeError):
    print("Not on RPi.  Can't access camera.")

import settings
import tasks


class Camera(PiCamera):
    """Pi camera configured for DoorPi."""

    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)
        self.rotation = settings.CAMERA_ROTATION
        self.resolution = settings.CAMERA_RESOLUTION
        self.framerate = settings.CAMERA_FRAMERATE
        self.thread_lock = threading.Lock()
        self.recording_thread = None
        self.scanner = None

    @staticmethod
    def get_video_path():
        # returns the absolute path for new video files based on a timestamp
        return settings.VIDEO_PATH + "%s.h264" % datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def start_recording(self, format=None, resize=None, splitter_port=1, **options):
        output = self.get_video_path()
        super(Camera, self).start_recording(output, format, resize, splitter_port, **options)

        record_time = settings.CAMERA_RECORD_TIME
        while record_time > 0:
            if self.scanner.stop_scan:
                if self.recording:
                    self.stop_recording()
                    return
            record_time -= 1
            time.sleep(1)

        if self.recording:
            self.stop_recording()

    def record_event(self):
        self.recording_thread = threading.Thread(target=self.start_recording, name='CameraThread')
        self.recording_thread.start()
        logging.info('Starting recording...')
        logging.debug(threading.enumerate())

    def activate(self):
        logging.debug('Camera Activated.')
        with self.thread_lock:
            if not self.recording_thread:
                self.record_event()
            elif not self.recording_thread.is_alive():
                self.record_event()
                tasks.send_LED_command.delay(settings.LED_ALARM_COMMAND)