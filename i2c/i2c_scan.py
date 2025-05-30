#!/usr/bin/env python3
import smbus2
import sys
import os
import time

def scan_i2c_bus(bus_number=1):
    """Escaneia o barramento I2C e retorna todos os endereços de dispositivos encontrados"""
    print(f"Escaneando barramento I2C-{bus_number} completo (endereços 0x03-0x77)...")
    
    try:
        bus = smbus2.SMBus(bus_number)
        found_devices = []
        
        # Matriz para exibição dos dispositivos encontrados
        address_grid = []
        for i in range(8):
            row = []
            for j in range(16):
                row.append("--")
            address_grid.append(row)
            
        # Teste cada endereço possível no barramento I2C
        for addr in range(0x03, 0x78):
            try:
                # Tenta ler um byte para ver se o dispositivo responde
                bus.read_byte(addr)
                # Se chegou aqui, um dispositivo foi encontrado
                found_devices.append(addr)
                
                # Preenche a matriz
                row = addr // 16
                col = addr % 16
                address_grid[row][col] = f"{addr:02X}"
                
            except Exception:
                pass
                
        bus.close()
        
        # Mostra um cabeçalho
        print("\n     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F")
        print("    -----------------------------------------------")
        
        # Exibe a matriz formatada
        for i in range(8):
            row_prefix = f"{i:X}0: "
            print(row_prefix + " ".join(address_grid[i]))
            
        # Mostra os dispositivos encontrados de forma mais amigável
        if found_devices:
            print(f"\nForam encontrados {len(found_devices)} dispositivos I2C:")
            for addr in found_devices:
                device_name = get_device_name(addr)
                print(f"  • Endereço 0x{addr:02X} - {device_name}")
        else:
            print("\nNenhum dispositivo I2C encontrado!")
            
        return found_devices
        
    except Exception as e:
        print(f"Erro ao acessar o barramento I2C-{bus_number}: {e}")
        return []

def get_device_name(addr):
    """Retorna um nome provável para um dispositivo com base no endereço"""
    common_devices = {
        0x1D: "ADXL345 (Acelerômetro)",
        0x20: "PCF8574 (Expansor I/O)",
        0x23: "BH1750 (Sensor de Luz)",
        0x27: "PCF8574 (Controlador LCD)",
        0x29: "TSL2561 (Sensor de Luz)",
        0x3C: "SSD1306 (Display OLED)",
        0x40: "Si7021/HTU21D (Sensor de Umidade)",
        0x48: "ADS1115 (Conversor ADC)",
        0x50: "AT24C32 (EEPROM)",
        0x53: "ADXL345 (Acelerômetro)",
        0x68: "DS3231/MPU6050 (RTC/IMU)",
        0x76: "BMP280/BME280 (Sensor de Pressão/Temperatura)",
        0x77: "BMP280/BME280 (Sensor de Pressão/Temperatura)"
    }
    
    return common_devices.get(addr, "Dispositivo desconhecido")

def check_kernel_module():
    """Verifica se o módulo do kernel BMP280 está presente"""
    print("\nVerificando módulo do kernel BMP280...")
    
    # Verifica se o módulo está carregado - sem usar sudo
    try:
        # Usa cat /proc/modules em vez de lsmod para evitar potenciais problemas de permissão
        with os.popen("cat /proc/modules | grep bmp280") as f:
            output = f.read().strip()
            if output:
                print(f"✅ Módulo do kernel BMP280 está carregado: {output}")
            else:
                print("⚠️ Módulo do kernel BMP280 não está carregado")
    except Exception as e:
        print(f"Erro ao verificar módulo do kernel: {e}")
    
    # Verifica arquivos do dispositivo
    device_paths = [
        "/sys/bus/i2c/devices/i2c-1/1-0076/iio:device0/",
        "/sys/bus/i2c/devices/i2c-1/1-0077/iio:device1/",
        "/sys/bus/iio/devices/iio:device0/",
        "/sys/bus/iio/devices/iio:device1/"
    ]
    
    found_device = False
    for path in device_paths:
        if os.path.exists(path):
            temp_path = os.path.join(path, "in_temp_input")
            pressure_path = os.path.join(path, "in_pressure_input")
            
            if os.path.exists(temp_path) and os.path.exists(pressure_path):
                found_device = True
                print(f"✅ Dispositivo BMP280 encontrado via módulo do kernel em: {path}")
                try:
                    with open(temp_path, 'r') as f:
                        content = f.read().strip()
                        # Tenta converter para int, se falhar, tenta float
                        try:
                            temp_raw = int(content)
                            temp = (((temp_raw / 1000.0) * 100) + 0.5) / 100
                        except ValueError:
                            # Se o valor já for float, usa diretamente
                            temp = float(content)
                        print(f"  • Temperatura: {temp:.2f}°C")
                        
                    with open(pressure_path, 'r') as f:
                        content = f.read().strip()
                        try:
                            pressure_raw = int(content)
                            pressure = pressure_raw * 10
                        except ValueError:
                            # Se o valor já for float, usa diretamente
                            pressure = float(content)
                        print(f"  • Pressão: {pressure:.2f} hPa")
                except Exception as e:
                    print(f"  • Erro ao ler valores: {e}")
    
    if not found_device:
        print("⚠️ Nenhum dispositivo BMP280 encontrado via módulo do kernel")

def suggest_next_steps():
    """Sugere próximos passos com base nos resultados do diagnóstico"""
    print("\n" + "="*80)
    print("PRÓXIMOS PASSOS RECOMENDADOS")
    print("="*80)
    print("1. Verifique a conexão física do sensor BMP280:")
    print("   • Certifique-se de que o sensor está corretamente conectado ao barramento I2C")
    print("   • Verifique se os pinos VCC (3.3V), GND, SCL e SDA estão conectados corretamente")
    print("\n2. Se você estiver na placa rasp44, tente usar o módulo do kernel:")
    print("   • Modifique o código para usar use_kernel_module=True")
    print("   • Exemplo: sensor = BMP280Sensor(use_kernel_module=True)")
    print("\n3. Use o modo de simulação para continuar o desenvolvimento:")
    print("   • Modifique o código para usar simulation_mode=True")
    print("   • Exemplo: sensor = BMP280Sensor(simulation_mode=True)")
    print("\n4. Consulte o professor ou monitor do laboratório:")
    print("   • Peça ajuda para identificar se o sensor BMP280 está funcionando")
    print("   • Verifique se há um endereço alternativo específico para sua placa")
    print("="*80)

if __name__ == "__main__":
    print("\nDiagnóstico completo do sensor BMP280\n")
    
    # Verifica permissões do dispositivo I2C
    if os.path.exists("/dev/i2c-1"):
        print(f"✅ Dispositivo I2C encontrado em /dev/i2c-1")
        try:
            with open("/dev/i2c-1", "rb") as f:
                print("✅ Permissões de leitura OK para o dispositivo I2C")
        except PermissionError:
            print("❌ Sem permissões para acessar o dispositivo I2C")
            sys.exit(1)
    else:
        print("❌ Dispositivo I2C não encontrado")
        sys.exit(1)
    
    # Escaneia o barramento I2C
    found_devices = scan_i2c_bus()
    
    # Verifica módulo do kernel
    check_kernel_module()
    
    # Sugere próximos passos
    suggest_next_steps()
    
    # Se encontrou o BMP280, dê instruções específicas
    if 0x76 in found_devices or 0x77 in found_devices:
        addr = 0x76 if 0x76 in found_devices else 0x77
        print(f"\nSensor BMP280 encontrado no endereço 0x{addr:02X}!")
        print(f"Para usar este sensor, especifique o endereço correto:")
        print(f"sensor = BMP280Sensor(i2c_addr=0x{addr:02X})")
    else:
        print("\nPara utilizar o sensor no projeto, atualize i2c_module.py com:")
        print("from i2c_module import BMP280Sensor")
        print("# Use o modo de simulação enquanto o hardware não estiver disponível")
        print("sensor = BMP280Sensor(simulation_mode=True)")
