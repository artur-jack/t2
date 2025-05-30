import RPi.GPIO as GPIO

# Mapeamento dos botões
BUTTONS = {
    'up': 16,
    'down': 1,
    'left': 7,
    'right': 8,
    'emergency': 11
}

def setup_buttons():
    for pin in BUTTONS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_buttons():
    return {name: not GPIO.input(pin) for name, pin in BUTTONS.items()}
