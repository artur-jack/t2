# Módulo I2C para Sensor BMP280

Este módulo implementa a comunicação com o sensor BMP280 para leitura de temperatura e pressão atmosférica, compatível com o Trabalho 2 de Sistemas Embarcados.

## Visão Geral

O módulo suporta três modos de comunicação com o sensor BMP280:

1. **Módulo do Kernel** (recomendado): Lê dados do sensor através dos arquivos de dispositivo do kernel Linux
2. **I2C Direto**: Comunicação direta com o sensor via I2C usando as bibliotecas smbus2 e bmp280
3. **Simulação**: Gera valores simulados quando o hardware não está disponível

## Arquivos do Projeto

- **i2c_module.py**: Módulo principal com a classe BMP280Sensor
- **test_bmp280.py**: Script para testar o funcionamento do sensor
- **i2c_scan.py**: Ferramenta para diagnosticar o barramento I2C e detectar dispositivos

## Requisitos

```bash
pip install smbus2 bmp280
```

## Como Usar

### 1. Diagnóstico do Barramento I2C

Para verificar a presença do sensor e outros dispositivos I2C:

```bash
python i2c_scan.py
```

### 2. Testar o Sensor BMP280

```bash
# Usar o melhor método disponível (recomendado)
python test_bmp280.py

# Forçar o uso do módulo do kernel
python test_bmp280.py --kernel

# Forçar o uso do I2C direto
python test_bmp280.py --i2c

# Usar modo de simulação
python test_bmp280.py --simulate
```

### 3. Integração com o Projeto Principal

```python
from i2c_module import BMP280Sensor

# Inicializa o sensor (usando automaticamente o melhor método disponível)
sensor = BMP280Sensor()

# Lê temperatura e pressão
temperatura = sensor.read_temperature()
pressao = sensor.read_pressure()

print(f"Temperatura: {temperatura:.2f}°C")
print(f"Pressão: {pressao:.2f} hPa")

# Fecha a conexão quando terminar
sensor.close()
```

## Detecção de Dispositivos

O sensor BMP280 normalmente está nos endereços 0x76 ou 0x77. Na sua placa, ele foi detectado via módulo do kernel nos diretórios:
- `/sys/bus/i2c/devices/i2c-1/1-0076/iio:device0/`
- `/sys/bus/iio/devices/iio:device0/`

## Solução de Problemas

Se o sensor não for detectado corretamente:

1. Verifique as conexões físicas do sensor
2. Use o modo de simulação para desenvolvimento
3. Verifique se você está no grupo i2c (você já está: `flaviomelo` no grupo `i2c`)

## Mais Informações

Consulte o código-fonte para opções adicionais e detalhes de implementação.
