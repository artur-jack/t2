# encoder.py
import RPi.GPIO as GPIO
import threading
import time

# Estado dos encoders (posição absoluta)
pos_x = 0
pos_y = 0

# Pinos
PIN_X_A = 5
PIN_X_B = 6
PIN_Y_A = 12
PIN_Y_B = 13

def _encoder_callback_x(channel):
    global pos_x
    b = GPIO.input(PIN_X_B)
    if b == GPIO.HIGH:
        pos_x += 1
    else:
        pos_x -= 1

def _encoder_callback_y(channel):
    global pos_y
    b = GPIO.input(PIN_Y_B)
    if b == GPIO.HIGH:
        pos_y += 1
    else:
        pos_y -= 1

def setup_encoder_interrupts():
    GPIO.add_event_detect(PIN_X_A, GPIO.BOTH, callback=_encoder_callback_x)
    GPIO.add_event_detect(PIN_Y_A, GPIO.BOTH, callback=_encoder_callback_y)

def reset_position():
    global pos_x, pos_y
    pos_x = 0
    pos_y = 0

def get_position():
    return pos_x, pos_y
