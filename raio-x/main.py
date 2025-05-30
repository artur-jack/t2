from gpio.gpio_config import setup_gpio, cleanup_gpio
from gpio.buttons import setup_buttons, read_buttons
from gpio.limitswitches import setup_limit_switches, read_limit_switches

import time

def main():
    try:
        setup_gpio()
        setup_buttons()
        setup_limit_switches()

        print("Pressione Ctrl+C para sair")

        while True:
            buttons = read_buttons()
            limits = read_limit_switches()

            print("Botões:", buttons, " Fim de Curso:", limits)
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Encerrando com segurança...")

    finally:
        cleanup_gpio()

if __name__ == "__main__":
    main()
