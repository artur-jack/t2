#!/usr/bin/env python3
import time
import argparse
from i2c_module import BMP280Sensor

def main():
    parser = argparse.ArgumentParser(description='Teste do sensor BMP280 para Trabalho 2')
    parser.add_argument('--i2c', action='store_true', help='Forçar uso do I2C direto')
    parser.add_argument('--kernel', action='store_true', help='Forçar uso do módulo do kernel')
    parser.add_argument('--simulate', action='store_true', help='Usar modo de simulação')
    parser.add_argument('--count', type=int, default=20, help='Número de leituras')
    parser.add_argument('--interval', type=float, default=0.5, help='Intervalo entre leituras (s)')
    args = parser.parse_args()
    
    print("\n=== Teste do Sensor BMP280 para o Trabalho 2 ===\n")
    
    # Determina o modo baseado nos argumentos
    if args.simulate:
        print("Modo: Simulação")
        sensor = BMP280Sensor(simulation_mode=True)
    elif args.i2c:
        print("Modo: I2C Direto")
        try:
            sensor = BMP280Sensor(use_kernel_module=False)
        except Exception as e:
            print(f"Erro ao inicializar I2C direto: {e}")
            print("Caindo para modo de simulação...")
            sensor = BMP280Sensor(simulation_mode=True)
    elif args.kernel:
        print("Modo: Módulo do Kernel")
        try:
            sensor = BMP280Sensor(use_kernel_module=True)
        except Exception as e:
            print(f"Erro ao inicializar módulo do kernel: {e}")
            print("Caindo para modo de simulação...")
            sensor = BMP280Sensor(simulation_mode=True)
    else:
        print("Modo: Automático (tentando kernel primeiro)")
        # Conforme o diagnóstico, o kernel module está funcionando
        try:
            sensor = BMP280Sensor(use_kernel_module=True)
        except Exception as e:
            print(f"Erro ao inicializar módulo do kernel: {e}")
            print("Tentando I2C direto...")
            try:
                sensor = BMP280Sensor(use_kernel_module=False)
            except Exception as e2:
                print(f"Erro ao inicializar I2C direto: {e2}")
                print("Caindo para modo de simulação...")
                sensor = BMP280Sensor(simulation_mode=True)
    
    # Cabeçalho da tabela
    print("\n{:<4} | {:<12} | {:<12}".format("Nº", "Temperatura", "Pressão"))
    print("-" * 33)
    
    # Realiza leituras
    try:
        for i in range(args.count):
            temp = sensor.read_temperature()
            pressure = sensor.read_pressure()
            print("{:<4} | {:<12} | {:<12}".format(
                i+1, 
                f"{temp:.2f}°C", 
                f"{pressure:.2f} hPa"
            ))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nLeitura interrompida pelo usuário")
    finally:
        sensor.close()
    
    print("\n=== Usando o BMP280 no projeto ===")
    print("Para integrar o sensor no projeto principal:")
    print("""
from i2c_module import BMP280Sensor

# Inicializa o sensor (usando o módulo do kernel por padrão)
sensor = BMP280Sensor()

# Lê valores de temperatura e pressão
temp = sensor.read_temperature()
pressure = sensor.read_pressure()

# Envia dados para o painel via MODBUS
# ... código para enviar os dados ...

# Não esqueça de fechar a conexão quando terminar
sensor.close()
""")
    
    return 0

if __name__ == "__main__":
    exit(main())
