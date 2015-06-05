# the address and port of your doorpi web server
HTTP_SERVER_URL = 'http://doorpi:5000'
HTTP_SERVER_PORT = 5000

# camera settings
CAMERA_ROTATION = 180
CAMERA_RESOLUTION = (1400, 1400)
CAMERA_FRAMERATE = 15
CAMERA_RECORD_TIME = 5

# check that these directories and files exist
VIDEO_PATH = "/home/pi/camera/"
STATUS_FILE_PATH = "/var/lib/misc/alarm"
LOG_FILE_PATH = "/var/log/alarm/alarm.log"

# secret key for flask session authentication
FLASK_SESSION_KEY = 'CREATE A NEW KEY AND PUT IT HERE'

# sensor config
MOTION_SENSOR = {'pin': 18,
                 'name': 'Motion Hallway'}

DOOR_SENSOR = {'pin': 23,
               'pull_up': True,
               'name': 'Door'}

SENSORS = [MOTION_SENSOR, DOOR_SENSOR]
SENSOR_REFRESH_RATE = .25

# alarm state keywords
ARMED = 'ARMED'
DISARMED = 'DISARMED'

# LED config
LED_DEVICE_PATH = '/dev/ttyACM0'
LED_DEVICE_BAUDRATE = 9600

LED_COUNTUP_COMMAND = 'c'
LED_COUNTDOWN_COMMAND = 'w'
LED_ALARM_COMMAND = 'm'
LED_STOP_COMMAND = 'T'
LED_DISARMED_COMMAND = 'r'

# number of seconds for the ARMING countdown
COUNTDOWN_DURATION = 18

# sound file paths
ARMING_SOUND_FILE = 'doorsounds/armingsystem.mp3'
ARMED_SOUND_FILE = 'doorsounds/systemarmed.mp3'
DISARMED_SOUND_FILE = 'doorsounds/systemdisarmed.mp3'
ENTRY_SOUND_FILE = 'doorsounds/unauthorizedaccess.mp3'
NOTIFICATION_SOUND_FILE = 'doorsounds/callingpolice.mp3'

# email config
EMAIL_RECIPIENTS = ('youremailrecipient@example.com', '')
EMAIL_SERVER_URL = 'smtp.example.com'
EMAIL_SERVER_PORT = 587
EMAIL_USERNAME = 'doorpiusername@example.com'
EMAIL_PASSWORD = 'doorpiemailpassword'
EMAIL_MESSAGE = "Entry detected at <time>.\nSensor: <sensor>"
EMAIL_TIME_FORMAT = '%m/%d/%Y %I:%M:%S %p'