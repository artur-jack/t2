import RPi.GPIO as GPIO

# Pinos dos motores conforme a tabela do README
MOTOR_PINS = {
    'x_pwm': 17,
    'x_dir1': 27,
    'x_dir2': 22,
    'y_pwm': 23,
    'y_dir1': 24,
    'y_dir2': 25,
    'raio_x': 18  # Pino para acionamento do raio-X (captura)
}

# Frequência PWM (1 kHz conforme especificado)
PWM_FREQ = 1000

# Objetos PWM
pwm_x = None
pwm_y = None

def setup_motors():
    """Configura os pinos dos motores e inicializa o PWM"""
    # Configurar pinos como saída
    for pin in MOTOR_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    
    # Inicializar PWM
    global pwm_x, pwm_y
    pwm_x = GPIO.PWM(MOTOR_PINS['x_pwm'], PWM_FREQ)
    pwm_y = GPIO.PWM(MOTOR_PINS['y_pwm'], PWM_FREQ)
    
    # Iniciar PWM com duty cycle 0 (motor parado)
    pwm_x.start(0)
    pwm_y.start(0)

def set_motor_direction(motor, direction):
    """
    Define a direção do motor
    
    Args:
        motor (str): 'x' ou 'y'
        direction (int): 1 para frente, -1 para trás, 0 para parar
    """
    if motor == 'x':
        dir1_pin = MOTOR_PINS['x_dir1']
        dir2_pin = MOTOR_PINS['x_dir2']
    else:  # motor == 'y'
        dir1_pin = MOTOR_PINS['y_dir1']
        dir2_pin = MOTOR_PINS['y_dir2']
    
    if direction == 1:  # Frente
        GPIO.output(dir1_pin, GPIO.HIGH)
        GPIO.output(dir2_pin, GPIO.LOW)
    elif direction == -1:  # Trás
        GPIO.output(dir1_pin, GPIO.LOW)
        GPIO.output(dir2_pin, GPIO.HIGH)
    else:  # Parar (direction == 0)
        GPIO.output(dir1_pin, GPIO.LOW)
        GPIO.output(dir2_pin, GPIO.LOW)

def set_motor_speed(motor, speed):
    """
    Define a velocidade do motor usando PWM
    
    Args:
        motor (str): 'x' ou 'y'
        speed (float): Velocidade do motor (0 a 100)
    """
    # Garantir que a velocidade está entre 0 e 100
    speed = max(0, min(100, speed))
    
    if motor == 'x':
        pwm_x.ChangeDutyCycle(speed)
    else:  # motor == 'y'
        pwm_y.ChangeDutyCycle(speed)

def stop_motors():
    """Para todos os motores"""
    set_motor_direction('x', 0)
    set_motor_direction('y', 0)
    set_motor_speed('x', 0)
    set_motor_speed('y', 0)

def activate_raio_x(activate=True):
    """
    Ativa ou desativa o raio-X (captura de imagem)
    
    Args:
        activate (bool): True para ativar, False para desativar
    """
    GPIO.output(MOTOR_PINS['raio_x'], GPIO.HIGH if activate else GPIO.LOW)
