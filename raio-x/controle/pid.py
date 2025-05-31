import time
from gpio.motors import set_motor_direction, set_motor_speed
from controle.encoder import get_position

class PIDController:
    def __init__(self, kp=0.5, ki=0.05, kd=40.0):
        # Constantes PID conforme sugerido no README
        self.kp = kp  # Ganho proporcional
        self.ki = ki  # Ganho integral
        self.kd = kd  # Ganho derivativo
        
        # Variáveis de estado para cada eixo
        self.reset()
    
    def reset(self):
        """Reseta as variáveis de estado do controlador"""
        # Para eixo X
        self.x_setpoint = 0      # Posição desejada
        self.x_prev_error = 0    # Erro anterior
        self.x_integral = 0      # Acumulador integral
        self.x_last_time = time.time()  # Tempo da última atualização
        
        # Para eixo Y
        self.y_setpoint = 0
        self.y_prev_error = 0
        self.y_integral = 0
        self.y_last_time = time.time()
    
    def set_target_position(self, x=None, y=None):
        """Define a posição alvo (setpoint) para um ou ambos os eixos"""
        if x is not None:
            self.x_setpoint = x
        if y is not None:
            self.y_setpoint = y
    
    def compute_pid(self, axis, current_position, setpoint):
        """
        Calcula o valor de controle PID para um eixo
        
        Args:
            axis (str): 'x' ou 'y'
            current_position (int): Posição atual do encoder
            setpoint (int): Posição desejada
            
        Returns:
            tuple: (direção, velocidade) onde direção é 1, -1 ou 0 e velocidade é 0-100
        """
        # Calcular o erro
        error = setpoint - current_position
        
        # Obter o tempo atual e calcular dt
        current_time = time.time()
        if axis == 'x':
            dt = current_time - self.x_last_time
            self.x_last_time = current_time
            
            # Calcular termo integral (com anti-windup)
            self.x_integral += error * dt
            # Limitar o termo integral para evitar acúmulo excessivo
            self.x_integral = max(-100, min(100, self.x_integral))
            
            # Calcular termo derivativo
            derivative = (error - self.x_prev_error) / dt if dt > 0 else 0
            self.x_prev_error = error
        else:  # axis == 'y'
            dt = current_time - self.y_last_time
            self.y_last_time = current_time
            
            self.y_integral += error * dt
            self.y_integral = max(-100, min(100, self.y_integral))
            
            derivative = (error - self.y_prev_error) / dt if dt > 0 else 0
            self.y_prev_error = error
        
        # Calcular saída PID
        output = (self.kp * error) + (self.ki * (self.x_integral if axis == 'x' else self.y_integral)) + (self.kd * derivative)
        
        # Determinar direção e velocidade
        if abs(error) < 2:  # Margem de erro pequena, considerar como posição atingida
            return 0, 0
        
        direction = 1 if output > 0 else -1
        speed = min(abs(output), 100)  # Limitar velocidade entre 0 e 100
        
        return direction, speed
    
    def update(self):
        """
        Atualiza o controle PID para ambos os eixos e aplica aos motores
        
        Returns:
            tuple: ((erro_x, velocidade_x), (erro_y, velocidade_y))
        """
        # Obter posição atual
        pos_x, pos_y = get_position()
        
        # Calcular controle para eixo X
        x_direction, x_speed = self.compute_pid('x', pos_x, self.x_setpoint)
        set_motor_direction('x', x_direction)
        set_motor_speed('x', x_speed)
        
        # Calcular controle para eixo Y
        y_direction, y_speed = self.compute_pid('y', pos_y, self.y_setpoint)
        set_motor_direction('y', y_direction)
        set_motor_speed('y', y_speed)
        
        # Calcular erros
        error_x = self.x_setpoint - pos_x
        error_y = self.y_setpoint - pos_y
        
        return (error_x, x_speed), (error_y, y_speed)
    
    def is_position_reached(self, tolerance=5):
        """
        Verifica se a posição desejada foi atingida dentro de uma tolerância
        
        Args:
            tolerance (int): Tolerância em unidades do encoder
            
        Returns:
            bool: True se ambos os eixos atingiram a posição desejada
        """
        pos_x, pos_y = get_position()
        x_reached = abs(self.x_setpoint - pos_x) <= tolerance
        y_reached = abs(self.y_setpoint - pos_y) <= tolerance
        return x_reached and y_reached
