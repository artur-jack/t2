from gpio.gpio_config import setup_gpio, cleanup_gpio
from gpio.buttons import setup_buttons, read_buttons
from gpio.limitswitches import setup_limit_switches, read_limit_switches
from gpio.encoder_gpio import setup_encoders
from controle.encoder import setup_encoder_interrupts, get_position

import time

def main():
    try:
        setup_gpio()
        setup_buttons()
        setup_limit_switches()
        setup_encoders()
        setup_encoder_interrupts()

        print("Pressione Ctrl+C para sair")

        while True:
            buttons = read_buttons()
            limits = read_limit_switches()
            pos_x, pos_y = get_position()

            print("Botões:", buttons,
                  " Fim de Curso:", limits,
                  f" Posição X: {pos_x} | Posição Y: {pos_y}")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Encerrando com segurança...")

    finally:
        cleanup_gpio()

if __name__ == "__main__":
    main()

