import time
import os
import sys
import logging
import random

# Configurando o logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("I2C_Module")

# Tentativa condicional de importar bibliotecas específicas do I2C
try:
    import smbus2
    import bmp280
    I2C_LIBRARIES_AVAILABLE = True
except ImportError:
    I2C_LIBRARIES_AVAILABLE = False
    logger.warning("Bibliotecas smbus2/bmp280 não encontradas. Modo de simulação será usado.")

class BMP280Sensor:
    def __init__(self, use_kernel_module=True, i2c_addr=0x76, i2c_bus=1, simulation_mode=False):
        """
        Inicializa o sensor BMP280.
        
        Args:
            use_kernel_module (bool): Se True, usa o módulo do kernel para leitura,
                                     se False, usa acesso direto I2C.
            i2c_addr (int): Endereço I2C do sensor (geralmente 0x76 ou 0x77)
            i2c_bus (int): Número do barramento I2C (geralmente 1 para Raspberry Pi)
            simulation_mode (bool): Se True, gera valores simulados em vez de ler hardware
        """
        self.use_kernel_module = use_kernel_module
        self.i2c_addr = i2c_addr
        self.i2c_bus = i2c_bus
        self.sensor = None
        self.kernel_temp_path = None
        self.kernel_pressure_path = None
        self.simulation_mode = simulation_mode or not I2C_LIBRARIES_AVAILABLE
        self.bus = None
        
        # Valores iniciais para simulação
        self.simulated_temp = 25.0
        self.simulated_pressure = 1013.25
        self.simulation_trend = 0.1  # Tendência de temperatura
        self.last_update = time.time()
        
        # Se for modo de simulação, não tenta inicializar hardware
        if self.simulation_mode:
            logger.info("Modo de simulação ativado. Valores serão gerados com variação realista.")
            return
            
        try:
            if self.use_kernel_module:
                self._initialize_kernel_module()
            else:
                self._initialize_i2c()
        except Exception as e:
            logger.error(f"Erro ao inicializar o sensor BMP280: {e}")
            logger.info("Tentando ativar modo de simulação automaticamente...")
            self.simulation_mode = True

    def _initialize_i2c(self):
        """Inicializa a comunicação I2C direta com o sensor BMP280."""
        if not I2C_LIBRARIES_AVAILABLE:
            raise ImportError("Bibliotecas smbus2/bmp280 não estão instaladas")
            
        # Primeiro, verifica se o barramento especificado existe
        if not os.path.exists(f"/dev/i2c-{self.i2c_bus}"):
            raise FileNotFoundError(f"Barramento I2C-{self.i2c_bus} não encontrado")
        
        try:
            self.bus = smbus2.SMBus(self.i2c_bus)
            
            # Tenta verificar se o dispositivo está presente no barramento
            try:
                self.bus.read_byte(self.i2c_addr)
            except OSError:
                # Se falhar, tenta o endereço alternativo comum (0x76 ou 0x77)
                alt_addr = 0x77 if self.i2c_addr == 0x76 else 0x76
                logger.info(f"Dispositivo não encontrado em 0x{self.i2c_addr:02x}, tentando 0x{alt_addr:02x}")
                try:
                    self.bus.read_byte(alt_addr)
                    self.i2c_addr = alt_addr
                except OSError:
                    logger.warning(f"Sensor BMP280 não encontrado nos endereços 0x76 ou 0x77")
                    logger.info("Tentando usar o módulo do kernel...")
                    self.use_kernel_module = True
                    self._initialize_kernel_module()
                    return
            
            self.sensor = bmp280.BMP280(i2c_dev=self.bus, i2c_addr=self.i2c_addr)
            logger.info(f"Sensor BMP280 inicializado com sucesso via I2C direto (barramento: {self.i2c_bus}, endereço: 0x{self.i2c_addr:02x})")
        except Exception as e:
            if self.bus:
                self.bus.close()
            logger.error(f"Erro ao inicializar I2C: {e}")
            raise

    def _initialize_kernel_module(self):
        """Inicializa a comunicação via módulo do kernel."""
        try:
            # Busca pelos diretórios do dispositivo
            device_paths = [
                "/sys/bus/i2c/devices/i2c-1/1-0076/iio:device0/",
                "/sys/bus/i2c/devices/i2c-1/1-0077/iio:device1/",
                "/sys/bus/iio/devices/iio:device0/",
                "/sys/bus/iio/devices/iio:device1/"
            ]
            
            for path in device_paths:
                if os.path.exists(path):
                    temp_path = os.path.join(path, "in_temp_input")
                    pressure_path = os.path.join(path, "in_pressure_input")
                    
                    if os.path.exists(temp_path):
                        self.kernel_temp_path = temp_path
                        logger.info(f"Arquivo de temperatura BMP280 encontrado em: {temp_path}")
                    
                    if os.path.exists(pressure_path):
                        self.kernel_pressure_path = pressure_path
                        logger.info(f"Arquivo de pressão BMP280 encontrado em: {pressure_path}")
                    
                    if self.kernel_temp_path or self.kernel_pressure_path:
                        logger.info(f"Dispositivo BMP280 encontrado em: {path}")
                        break
            
            if not self.kernel_temp_path:
                raise FileNotFoundError("Arquivos de temperatura do módulo do kernel BMP280 não encontrados.")
                
            logger.info("Sensor BMP280 inicializado com sucesso via módulo do kernel")
        except Exception as e:
            logger.error(f"Erro ao inicializar módulo do kernel: {e}")
            raise

    def _update_simulation(self):
        """Atualiza os valores simulados para criar variações realistas"""
        current_time = time.time()
        elapsed = current_time - self.last_update
        
        if elapsed > 0.1:  # Atualiza a cada 100ms no máximo
            # Simulação de temperatura com variação realista
            random_change = random.uniform(-0.05, 0.05)
            trend_change = self.simulation_trend * elapsed * 0.1
            
            self.simulated_temp += random_change + trend_change
            
            # Inverte a tendência ao atingir limites
            if self.simulated_temp > 30:
                self.simulation_trend = -abs(self.simulation_trend)
            elif self.simulated_temp < 15:
                self.simulation_trend = abs(self.simulation_trend)
                
            # Limita a faixa de temperatura entre 10°C e 35°C
            self.simulated_temp = max(10, min(35, self.simulated_temp))
            
            # Simulação de pressão atmosférica
            pressure_change = random.uniform(-0.1, 0.1) - trend_change * 2
            self.simulated_pressure += pressure_change
            
            # Limita a faixa de pressão entre 990 e 1030 hPa
            self.simulated_pressure = max(990, min(1030, self.simulated_pressure))
            
            self.last_update = current_time

    def read_temperature(self):
        """
        Lê a temperatura do sensor BMP280.
        
        Returns:
            float: Temperatura em graus Celsius
        """
        try:
            if self.simulation_mode:
                # Atualiza valores simulados
                self._update_simulation()
                temperature = self.simulated_temp
            elif self.use_kernel_module:
                # Lê o valor do arquivo do kernel
                with open(self.kernel_temp_path, 'r') as f:
                    temp_data = f.read().strip()
                    try:
                        # Tenta converter para inteiro primeiro (formato padrão)
                        temp_raw = int(temp_data)
                        temperature = (((temp_raw / 1000.0) * 100) + 0.5) / 100
                    except ValueError:
                        # Se falhar, tenta interpretar como float diretamente
                        try:
                            temperature = float(temp_data)
                        except ValueError:
                            logger.error(f"Formato de temperatura não reconhecido: {temp_data}")
                            temperature = 25.0  # Valor padrão em caso de erro
            else:
                temperature = self.sensor.get_temperature()
            
            logger.debug(f"Temperatura lida: {temperature:.2f}°C")
            return round(temperature, 2)
        except Exception as e:
            logger.error(f"Erro ao ler temperatura: {e}")
            # Retorna um valor padrão em caso de erro
            return 25.0

    def read_pressure(self):
        """
        Lê a pressão atmosférica do sensor BMP280.
        
        Returns:
            float: Pressão em hPa (hectopascal)
        """
        try:
            if self.simulation_mode:
                # Atualiza valores simulados
                self._update_simulation()
                pressure = self.simulated_pressure
            elif self.use_kernel_module and self.kernel_pressure_path:
                # Lê o valor do arquivo do kernel
                with open(self.kernel_pressure_path, 'r') as f:
                    pressure_data = f.read().strip()
                    try:
                        # Tenta converter para inteiro primeiro (formato padrão)
                        pressure_raw = int(pressure_data)
                        pressure = pressure_raw * 10  # Multiplicar por 10 conforme documentação
                    except ValueError:
                        # Se falhar, tenta interpretar como float diretamente
                        try:
                            pressure = float(pressure_data)
                        except ValueError:
                            logger.error(f"Formato de pressão não reconhecido: {pressure_data}")
                            pressure = 1013.25  # Valor padrão em caso de erro
            else:
                pressure = self.sensor.get_pressure()
            
            logger.debug(f"Pressão lida: {pressure:.2f} hPa")
            return round(pressure, 2)
        except Exception as e:
            logger.error(f"Erro ao ler pressão: {e}")
            # Retorna um valor padrão em caso de erro
            return 1013.25

    def read_all(self):
        """
        Lê temperatura e pressão do sensor BMP280.
        
        Returns:
            dict: Dicionário com os valores de temperatura e pressão
        """
        return {
            "temperature": self.read_temperature(),
            "pressure": self.read_pressure()
        }

    def close(self):
        """Fecha a conexão com o barramento I2C se estiver usando acesso direto."""
        if not self.use_kernel_module and self.bus and not self.simulation_mode:
            try:
                self.bus.close()
                logger.info("Conexão I2C fechada")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão I2C: {e}")


# Exemplo de uso do módulo
if __name__ == "__main__":
    try:
        # Verifica argumentos de linha de comando
        kernel_mode = "--kernel" in sys.argv or "-k" in sys.argv
        simulate = "--simulate" in sys.argv or "-s" in sys.argv
        
        if simulate:
            print("Executando em modo de simulação (valores gerados aleatoriamente)")
            sensor = BMP280Sensor(simulation_mode=True)
        elif kernel_mode:
            print("Tentando inicializar com módulo do kernel...")
            sensor = BMP280Sensor(use_kernel_module=True)
        else:
            # Por padrão, tenta o módulo do kernel primeiro, depois I2C direto
            print("Tentando inicializar com o melhor método disponível...")
            try:
                # Baseado no scan, o kernel module está funcionando
                sensor = BMP280Sensor(use_kernel_module=True)
            except Exception as e:
                print(f"Falha ao usar módulo do kernel: {e}")
                print("Tentando com acesso I2C direto...")
                try:
                    sensor = BMP280Sensor(use_kernel_module=False)
                except Exception as e2:
                    print(f"Falha ao usar I2C direto: {e2}")
                    print("Usando modo de simulação como alternativa...")
                    sensor = BMP280Sensor(simulation_mode=True)
        
        # Lê os valores algumas vezes
        for i in range(5):
            data = sensor.read_all()
            print(f"Leitura {i+1}: Temperatura: {data['temperature']:.2f}°C, Pressão: {data['pressure']:.2f} hPa")
            time.sleep(1)
            
        sensor.close()
        
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
