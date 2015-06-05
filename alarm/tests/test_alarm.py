import unittest
import time
import serial

import alarm
import settings
import routines
import sensor
import camera
import notifications
import led


print("WARNING: Before testing, make sure that the alarm service is not currently running on your pi!")


class ArmTestCase(unittest.TestCase):

    def setUp(self):
        self.alarm = alarm.Alarm()
        # start with alarm disarmed
        self.alarm.quickdisarm()

    def tearDown(self):
        self.alarm.quickdisarm()
        self.alarm = None

    def test_alarm_init(self):
        """Tests that the alarm can be initialized."""
        self.assertIsInstance(self.alarm, alarm.Alarm, "Couldn't initialize alarm.")

    def test_arm(self):
        """Tests that arming the alarm changes that status to settings.ARMED and starts the arm routine."""
        self.alarm.arm()
        self.assertIsInstance(self.alarm.current_routine, routines.ArmRoutine, "Arming did not start the ArmRoutine.")
        # wait for alarm to arm
        time.sleep(settings.COUNTDOWN_DURATION+5)
        self.assertEqual(self.alarm.status, settings.ARMED, "Arming did not change alarm status.")


class DisarmTestCase(unittest.TestCase):

    def setUp(self):
        self.alarm = alarm.Alarm()
        # start with alarm armed
        self.alarm.quickarm()
        # wait for arm
        time.sleep(5)

    def tearDown(self):
        self.alarm.quickdisarm()
        self.alarm = None

    def test_disarm(self):
        """Tests that disarming the alarm changes that status to settings.DISARMED."""
        self.alarm.disarm()
        self.assertEqual(self.alarm.status, settings.DISARMED, "Disarming did not change alarm status.")
        self.assertIsInstance(self.alarm.current_routine, routines.DisarmRoutine, "Disarming did not start the DisarmRoutine.")
        self.alarm.current_routine.cancel()


class RoutineTestCase(unittest.TestCase):

    def test_start_routine(self):
        """Tests that routines can be started and passed to Celery."""
        self.routine = routines.ArmRoutine()
        self.routine.start()
        # check that all tasks are submitted to celery
        self.assertEqual(len(self.routine.tasks), len(self.routine.submitted_tasks))
        # wait for tasks to complete
        time.sleep(sum(task[2] for task in self.routine.tasks) + 5)
        # check that celery completed all tasks
        for task in self.routine.submitted_tasks:
            self.assertEqual(task.status, 'SUCCESS')

        del self.routine

    def test_cancel_routines(self):
        """Tests that routines can be canceled and that tasks are revoked."""
        self.routine = routines.ArmRoutine()
        self.routine.start()

        # wait for the first 2 tasks to complete
        time.sleep(5)
        # check that celery completed the first 2 tasks
        for task in self.routine.submitted_tasks[:2]:
            self.assertEqual(task.status, 'SUCCESS')

        self.routine.cancel()
        self.assertTrue(self.routine.canceled)
        # wait for remaining tasks to be processed
        time.sleep(settings.COUNTDOWN_DURATION + 2)
        # check that the last 2 tasks were revoked
        for task in self.routine.submitted_tasks[2:]:
            self.assertEqual(task.status, 'REVOKED')

        del self.routine


class ScannerTestCase(unittest.TestCase):

    def test_scanner_start(self):
        """Tests that the scanner can be started."""
        self.scanner = sensor.Scanner()
        self.scanner.start()
        # check that the ScanThread is alive
        self.assertTrue(self.scanner.scan_thread.is_alive())
        # check that camera was initialized
        self.assertIsInstance(self.scanner.camera, camera.Camera)
        # check that camera can create a file path
        self.assertIn(settings.VIDEO_PATH, self.scanner.camera.get_video_path())
        self.scanner.stop()
        del self.scanner

    def test_scanner_stop(self):
        """Tests that the scanner can be stopped."""
        self.scanner = sensor.Scanner()
        self.scanner.start()
        scan_thread = self.scanner.scan_thread
        time.sleep(3)
        self.scanner.stop()
        time.sleep(3)
        # check that scanner.scan_thread is None
        self.assertIsNone(self.scanner.scan_thread)
        # check that the thread is dead
        self.assertFalse(scan_thread.is_alive())

        del self.scanner


class EmailTestCase(unittest.TestCase):

    def test_email_server(self):
        """Tests that the app can connect to the email server."""
        self.email = notifications.EmailNotification('Test message.')
        # check the login response code
        self.assertEqual(self.email.smtp_response[0], 235)

        self.email.smtp_server.quit()
        del self.email


class LEDTestCase(unittest.TestCase):

    def test_LED_device(self):
        """Tests that the app can connect to the LED device."""
        with led.LEDRing() as r:
            self.assertIsInstance(r.serial_connection, serial.Serial)
            # if serial connection is not open, sending a command will cause an error
            r.send_command(settings.LED_ALARM_COMMAND)


class SoundTestCase(unittest.TestCase):

    def test_sound_mixer(self):
        """Tests that the app can initialize the pygame audio mixer."""
        import pygame.mixer as mix
        mix.init()
        # check that the mixer initialized
        self.assertIsNotNone(mix.get_init())
        # try to play a sound
        mix.music.load(settings.ARMED_SOUND_FILE)
        mix.music.play()
        while mix.music.get_busy():
            continue
        mix.quit()


if __name__ == '__main__':
    unittest.main()