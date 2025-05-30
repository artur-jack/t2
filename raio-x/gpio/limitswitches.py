import RPi.GPIO as GPIO

LIMIT_SWITCHES = {
    'x_min': 26,
    'x_max': 19,
    'y_min': 20,
    'y_max': 21
}

def setup_limit_switches():
    for pin in LIMIT_SWITCHES.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_limit_switches():
    return {name: not GPIO.input(pin) for name, pin in LIMIT_SWITCHES.items()}
