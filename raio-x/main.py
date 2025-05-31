from gpio.gpio_config import setup_gpio, cleanup_gpio
from gpio.buttons import setup_buttons, read_buttons
from gpio.limitswitches import setup_limit_switches, read_limit_switches
from gpio.encoder_gpio import setup_encoders
from gpio.motors import setup_motors, stop_motors
from controle.encoder import setup_encoder_interrupts, get_position
from controle.motor_control import MotorController

import time
import signal
import sys

# Controlador global para acesso no handler de sinal
motor_controller = None

def signal_handler(sig, frame):
    print("\nEncerrando com segurança...")
    if motor_controller:
        motor_controller.stop()
    cleanup_gpio()
    sys.exit(0)

def main():
    global motor_controller
    
    try:
        # Configurar GPIO e periféricos
        setup_gpio()
        setup_buttons()
        setup_limit_switches()
        setup_encoders()
        setup_encoder_interrupts()
        
        # Inicializar controlador de motor
        motor_controller = MotorController()
        motor_controller.start()
        
        # Registrar handler para SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
        
        print("Sistema de controle da máquina de raio-X iniciado")
        print("Pressione Ctrl+C para sair")
        
        # Loop principal
        while True:
            # Ler estado dos botões
            buttons = read_buttons()
            
            # Processar comandos dos botões
            if buttons['up']:
                motor_controller.move_manual('up')
            elif buttons['down']:
                motor_controller.move_manual('down')
            elif buttons['left']:
                motor_controller.move_manual('left')
            elif buttons['right']:
                motor_controller.move_manual('right')
            elif buttons['emergency']:
                motor_controller.stop_movement()
            else:
                # Se nenhum botão está pressionado, parar os motores no modo manual
                if motor_controller.manual_mode:
                    motor_controller.stop_movement()
            
            # Obter informações do sistema
            limits = read_limit_switches()
            pos_x, pos_y = get_position()
            pos_x_m, pos_y_m = motor_controller.get_position_meters()
            speed_x_mps, speed_y_mps = motor_controller.get_speed_meters_per_second()
            
            # Exibir informações do sistema
            print(f"Posição: X={pos_x_m:.2f}m, Y={pos_y_m:.2f}m | "
                  f"Velocidade: X={speed_x_mps:.2f}m/s, Y={speed_y_mps:.2f}m/s | "
                  f"Modo: {'Manual' if motor_controller.manual_mode else 'Automático'} | "
                  f"Calibrado: {'Sim' if motor_controller.calibrated else 'Não'}")
            
            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.1)
    
    except Exception as e:
        print(f"Erro: {e}")
    
    finally:
        # Garantir que os motores sejam parados e GPIO limpo
        if motor_controller:
            motor_controller.stop()
        cleanup_gpio()

def test_motor_control():
    """Função para testar o controle básico dos motores"""
    global motor_controller
    
    try:
        # Configurar GPIO e periféricos
        setup_gpio()
        setup_buttons()
        setup_limit_switches()
        setup_encoders()
        setup_encoder_interrupts()
        
        # Inicializar controlador de motor
        motor_controller = MotorController()
        motor_controller.start()
        
        # Registrar handler para SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
        
        print("Teste de controle de motor iniciado")
        print("Pressione Ctrl+C para sair")
        
        # Testar movimento do motor X
        print("Movendo motor X para frente por 2 segundos...")
        motor_controller.move_manual('right')
        time.sleep(2)
        
        print("Parando motor X...")
        motor_controller.stop_movement()
        time.sleep(1)
        
        print("Movendo motor X para trás por 2 segundos...")
        motor_controller.move_manual('left')
        time.sleep(2)
        
        print("Parando motor X...")
        motor_controller.stop_movement()
        time.sleep(1)
        
        # Testar movimento do motor Y
        print("Movendo motor Y para cima por 2 segundos...")
        motor_controller.move_manual('up')
        time.sleep(2)
        
        print("Parando motor Y...")
        motor_controller.stop_movement()
        time.sleep(1)
        
        print("Movendo motor Y para baixo por 2 segundos...")
        motor_controller.move_manual('down')
        time.sleep(2)
        
        print("Parando motor Y...")
        motor_controller.stop_movement()
        
        print("Teste concluído!")
        
    except Exception as e:
        print(f"Erro no teste: {e}")
    
    finally:
        # Garantir que os motores sejam parados e GPIO limpo
        if motor_controller:
            motor_controller.stop()
        cleanup_gpio()

if __name__ == "__main__":
    # Para testar apenas o controle dos motores, descomente a linha abaixo
    test_motor_control()
    
    # Para executar o sistema completo
    # main()