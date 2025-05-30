import RPi.GPIO as GPIO

ENCODERS = {
    'x_a': 5,
    'x_b': 6,
    'y_a': 12,
    'y_b': 13
}

def setup_encoders():
    for pin in ENCODERS.values():
        GPIO.setup(pin, GPIO.IN)
