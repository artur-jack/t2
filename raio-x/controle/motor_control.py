import time
import threading
from gpio.motors import setup_motors, set_motor_direction, set_motor_speed, stop_motors, activate_raio_x
from gpio.limitswitches import read_limit_switches
from controle.encoder import get_position, reset_position
from controle.pid import PIDController

class MotorController:
    def __init__(self):
        self.pid = PIDController()
        self.running = False
        self.control_thread = None
        self.manual_mode = True  # Iniciar em modo manual
        self.calibrated = False
        self.saved_positions = {1: (0, 0), 2: (0, 0), 3: (0, 0), 4: (0, 0)}
        
        # Velocidades para modo manual (0-100)
        self.manual_speed_x = 50
        self.manual_speed_y = 50
        
        # Variáveis para cálculo de velocidade
        self.last_pos_x, self.last_pos_y = 0, 0
        self.last_time = time.time()
        self.speed_x, self.speed_y = 0, 0  # em unidades/segundo
        
        # Fator de conversão de unidades do encoder para metros
        # Este valor deve ser calibrado para seu sistema específico
        self.units_to_meters = 0.001  # exemplo: 1000 unidades = 1 metro
    
    def start(self):
        """Inicia o controlador de motor"""
        setup_motors()
        self.running = True
        self.control_thread = threading.Thread(target=self._control_loop)
        self.control_thread.daemon = True
        self.control_thread.start()
    
    def stop(self):
        """Para o controlador de motor"""
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=1.0)
        stop_motors()
    
    def _control_loop(self):
        """Loop principal de controle dos motores"""
        while self.running:
            # Verificar chaves de fim de curso
            limit_switches = read_limit_switches()
            
            # Calcular velocidade atual
            self._update_speed()
            
            if self.manual_mode:
                # No modo manual, o PID não é usado
                # O controle é feito diretamente pelos botões
                pass
            else:
                # No modo automático, atualizar o PID
                self.pid.update()
                
                # Verificar se chegou na posição desejada
                if self.pid.is_position_reached():
                    stop_motors()
            
            # Verificar limites de segurança
            self._check_safety_limits(limit_switches)
            
            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.01)
    
    def _update_speed(self):
        """Atualiza o cálculo de velocidade baseado na mudança de posição"""
        current_time = time.time()
        current_pos_x, current_pos_y = get_position()
        
        # Calcular o tempo decorrido
        dt = current_time - self.last_time
        if dt > 0:
            # Calcular velocidade em unidades/segundo
            self.speed_x = (current_pos_x - self.last_pos_x) / dt
            self.speed_y = (current_pos_y - self.last_pos_y) / dt
        
        # Atualizar valores anteriores
        self.last_pos_x, self.last_pos_y = current_pos_x, current_pos_y
        self.last_time = current_time
    
    def _check_safety_limits(self, limit_switches):
        """Verifica os limites de segurança e para os motores se necessário"""
        if limit_switches['x_min'] or limit_switches['x_max']:
            # Parar motor X se atingiu limite
            set_motor_speed('x', 0)
            
            # Se estiver no limite mínimo, não permitir movimento para esquerda
            if limit_switches['x_min']:
                # Permitir apenas movimento para direita
                if self.get_motor_direction('x') < 0:
                    set_motor_direction('x', 0)
            
            # Se estiver no limite máximo, não permitir movimento para direita
            if limit_switches['x_max']:
                # Permitir apenas movimento para esquerda
                if self.get_motor_direction('x') > 0:
                    set_motor_direction('x', 0)
        
        if limit_switches['y_min'] or limit_switches['y_max']:
            # Parar motor Y se atingiu limite
            set_motor_speed('y', 0)
            
            # Se estiver no limite mínimo, não permitir movimento para baixo
            if limit_switches['y_min']:
                # Permitir apenas movimento para cima
                if self.get_motor_direction('y') < 0:
                    set_motor_direction('y', 0)
            
            # Se estiver no limite máximo, não permitir movimento para cima
            if limit_switches['y_max']:
                # Permitir apenas movimento para baixo
                if self.get_motor_direction('y') > 0:
                    set_motor_direction('y', 0)
    
    def get_motor_direction(self, motor):
        """
        Retorna a direção atual do motor (implementação depende de como
        set_motor_direction está armazenando o estado)
        """
        # Esta é uma implementação simplificada
        # Na prática, você precisaria armazenar o estado atual da direção
        return 0  # Placeholder
    
    def move_manual(self, direction):
        """
        Move os motores manualmente na direção especificada
        
        Args:
            direction (str): 'up', 'down', 'left', 'right' ou 'stop'
        """
        if not self.manual_mode:
            return
        
        if direction == 'up':
            set_motor_direction('y', 1)
            set_motor_speed('y', self.manual_speed_y)
        elif direction == 'down':
            set_motor_direction('y', -1)
            set_motor_speed('y', self.manual_speed_y)
        elif direction == 'left':
            set_motor_direction('x', -1)
            set_motor_speed('x', self.manual_speed_x)
        elif direction == 'right':
            set_motor_direction('x', 1)
            set_motor_speed('x', self.manual_speed_x)
        elif direction == 'stop':
            stop_motors()
    
    def stop_movement(self):
        """Para o movimento de ambos os motores"""
        stop_motors()
    
    def set_mode(self, manual=True):
        """Define o modo de operação (manual ou automático)"""
        self.manual_mode = manual
        if manual:
            # Parar motores ao mudar para modo manual
            stop_motors()
        else:
            # Ao mudar para modo automático, manter a posição atual como alvo
            pos_x, pos_y = get_position()
            self.pid.set_target_position(pos_x, pos_y)
    
    def go_to_position(self, x=None, y=None):
        """
        Move para uma posição específica usando o controlador PID
        
        Args:
            x (int): Posição alvo no eixo X
            y (int): Posição alvo no eixo Y
        """
        # Mudar para modo automático
        self.manual_mode = False
        
        # Definir posição alvo
        self.pid.set_target_position(x, y)
    
    def go_to_saved_position(self, position_number):
        """
        Move para uma posição salva
        
        Args:
            position_number (int): Número da posição (1-4)
        """
        if 1 <= position_number <= 4 and position_number in self.saved_positions:
            x, y = self.saved_positions[position_number]
            self.go_to_position(x, y)
    
    def save_current_position(self, position_number):
        """
        Salva a posição atual como uma posição pré-definida
        
        Args:
            position_number (int): Número da posição (1-4)
        """
        if 1 <= position_number <= 4:
            pos_x, pos_y = get_position()
            self.saved_positions[position_number] = (pos_x, pos_y)
    
    def calibrate(self):
        """
        Realiza a calibração dos motores usando os sensores de fim de curso
        """
        # Implementação básica de calibração
        # 1. Mover para os limites mínimos
        # 2. Resetar os encoders
        # 3. Mover para o centro
        
        self.calibrated = False
        
        # Mover para o limite mínimo do eixo X
        set_motor_direction('x', -1)
        set_motor_speed('x', 30)  # Velocidade reduzida para calibração
        
        # Aguardar até atingir o limite
        while not read_limit_switches()['x_min'] and self.running:
            time.sleep(0.1)
        
        # Parar o motor X
        set_motor_speed('x', 0)
        
        # Mover para o limite mínimo do eixo Y
        set_motor_direction('y', -1)
        set_motor_speed('y', 30)
        
        # Aguardar até atingir o limite
        while not read_limit_switches()['y_min'] and self.running:
            time.sleep(0.1)
        
        # Parar o motor Y
        set_motor_speed('y', 0)
        
        # Resetar os encoders nesta posição
        reset_position()
        
        # Mover um pouco para o centro para sair dos sensores de fim de curso
        set_motor_direction('x', 1)
        set_motor_speed('x', 30)
        time.sleep(1)  # Mover por 1 segundo
        
        set_motor_direction('y', 1)
        set_motor_speed('y', 30)
        time.sleep(1)  # Mover por 1 segundo
        
        # Parar os motores
        stop_motors()
        
        self.calibrated = True
        
        # Definir a posição atual como alvo para o PID
        pos_x, pos_y = get_position()
        self.pid.set_target_position(pos_x, pos_y)
    
    def capture_image(self):
        """Ativa o raio-X para capturar uma imagem"""
        # Ativar o raio-X
        activate_raio_x(True)
        
        # Aguardar um tempo para a captura
        time.sleep(0.5)
        
        # Desativar o raio-X
        activate_raio_x(False)
    
    def get_position_meters(self):
        """
        Retorna a posição atual em metros
        
        Returns:
            tuple: (pos_x_m, pos_y_m) posição em metros
        """
        pos_x, pos_y = get_position()
        return pos_x * self.units_to_meters, pos_y * self.units_to_meters
    
    def get_speed_meters_per_second(self):
        """
        Retorna a velocidade atual em metros por segundo
        
        Returns:
            tuple: (speed_x_mps, speed_y_mps) velocidade em m/s
        """
        return self.speed_x * self.units_to_meters, self.speed_y * self.units_to_meters
