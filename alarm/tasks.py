from celery import Celery
import logging
import pygame.mixer as mix    # need to install pygame for python3 (RPi only has 2.7 installed by default)

import led
import notifications


app = Celery('tasks', backend='amqp', broker='amqp://')


@app.task
def send_LED_command(command):

    with led.LEDRing() as ring:
        ring.send_command(command)
        logging.debug('Sending LED command: %s', command)


@app.task
def play_sound(sound_file):

    mix.init()
    mix.music.load(sound_file)
    mix.music.play()
    while mix.music.get_busy():
        continue
    mix.quit()
    logging.debug('Playing sound: %s', sound_file)


@app.task
def send_email(message):
    with notifications.EmailNotification(message) as e:
        e.send()
        logging.info('Sending email.')
        logging.debug('Email message: %s', e)