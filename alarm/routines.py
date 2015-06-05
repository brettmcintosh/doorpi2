from datetime import datetime

import settings
import tasks


class BaseRoutine(object):

    def __init__(self):
        self.start_time = datetime.now()
        self.start_message = ''
        self.end_message = ''
        self.canceled = False
        self.tasks = ()
        self.submitted_tasks = []

    def seconds_since_start(self):
        time_since = datetime.now() - self.start_time
        return time_since.seconds

    def log(self):
        pass

    def start(self):
        for task in self.tasks:
            submitted_task = task[0].apply_async(kwargs=task[1], countdown=task[2])
            self.submitted_tasks.append(submitted_task)

    def cancel(self):
        if not self.done():
            self.canceled = True
            # stop any running LED commands
            tasks.send_LED_command(settings.LED_STOP_COMMAND)

            # revoke all pending celery tasks
            for task in self.submitted_tasks:
                task.revoke()

    def done(self):
        return all([t.ready() for t in self.submitted_tasks]) or self.canceled


class EntryRoutine(BaseRoutine):

    def __init__(self, msg):
        super(EntryRoutine, self).__init__()
        self.email_message = msg
        self.tasks = ((tasks.send_LED_command, {'command': settings.LED_COUNTDOWN_COMMAND}, 0),
                      (tasks.play_sound, {'sound_file': settings.ENTRY_SOUND_FILE}, 0),
                      (tasks.play_sound, {'sound_file': settings.ENTRY_SOUND_FILE}, 7),
                      (tasks.play_sound, {'sound_file': settings.ENTRY_SOUND_FILE}, 14),
                      (tasks.send_LED_command, {'command': settings.LED_ALARM_COMMAND}, 20),
                      (tasks.play_sound, {'sound_file': settings.NOTIFICATION_SOUND_FILE}, 20),
                      (tasks.send_email, {'message': self.email_message}, 20), )


class ArmRoutine(BaseRoutine):
    """
    -Play arm sound
    -LED count up
    -Wait 18 seconds
    -Play armed sound
    -LED armed
    """
    def __init__(self):
        super(ArmRoutine, self).__init__()
        self.tasks = ((tasks.send_LED_command, {'command': settings.LED_COUNTUP_COMMAND}, 0),
                      (tasks.play_sound, {'sound_file': settings.ARMING_SOUND_FILE}, 0),
                      (tasks.send_LED_command, {'command': settings.LED_ALARM_COMMAND}, settings.COUNTDOWN_DURATION),
                      (tasks.play_sound, {'sound_file': settings.ARMED_SOUND_FILE}, settings.COUNTDOWN_DURATION), )


class DisarmRoutine(BaseRoutine):
    """
    -Play disarm sound
    -LED disarmedSUCCESS
    """
    def __init__(self):
        super(DisarmRoutine, self).__init__()
        self.tasks = ((tasks.send_LED_command, {'command': settings.LED_DISARMED_COMMAND}, 0),
                      (tasks.play_sound, {'sound_file': settings.DISARMED_SOUND_FILE}, 0), )