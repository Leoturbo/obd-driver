import obd
import time
import serial

class OBDManager:
    def __init__(self):
        self.connection = None
        self.last_status = "Desconectado"
        self.is_ready = False

    # ==========================================
    # PASSO 4: ESTABELECIMENTO DO CANAL (ADAPTADO)
    # ==========================================
    def connect(self, target, protocolo="AUTO"):
        """
        No Windows/PC: target é 'COMx'
        No Android: target deve ser o Endereço MAC ou Porta Serial Bluetooth mapeada.
        """
        try:
            self.last_status = f"Iniciando Conexão em {target}..."
            print(self.last_status)

            # O python-obd tenta gerenciar o socket internamente.
            # Se target for um MAC (format XX:XX:XX:XX:XX:XX), ele tenta usar sockets bluetooth.
            self.connection = obd.OBD(
                portstr=target,
                baudrate=38400,
                protocol=protocolo,
                timeout=10,
                fast=False
            )

            if self.connection.is_connected():
                # PASSO 5: HANDSHAKE DE INICIALIZAÇÃO
                return self._handshake()
            else:
                self.last_status = "Falha: Adaptador não respondeu ao sinal."
                return False

        except Exception as ex:
            self.last_status = f"Erro de Hardware: {str(ex)}"
            print(f"Erro no Passo 4: {ex}")
            return False

    # ==========================================
    # PASSO 5: PROTOCOLO DE INICIALIZAÇÃO (HANDSHAKE)
    # ==========================================
    def _handshake(self):
        try:
            self.last_status = "Realizando Handshake (AT Z, E0, SP 0)..."

            # Comandos de inicialização manual para garantir prontidão do ELM327
            commands = [
                ("AT Z", "Resetando ELM327"),
                ("AT E0", "Desativando Eco"),
                ("AT SP 0", "Definindo Protocolo Automático")
            ]

            for cmd, desc in commands:
                print(f"Enviando {cmd}: {desc}")
                # O python-obd permite enviar comandos AT diretos via interface de baixo nível
                response = self.connection.interface.write(cmd.encode() + b"\r")
                time.sleep(1) # Aguarda processamento do ELM

            self.is_ready = True
            self.last_status = f"Pronto! Protocolo: {self.connection.protocol_name()}"
            return True

        except Exception as ex:
            self.last_status = "Erro no Handshake: ELM327 instável."
            print(f"Erro no Passo 5: {ex}")
            return False

    def disconnect(self):
        try:
            if self.connection:
                self.connection.close()
        except:
            pass
        finally:
            self.connection = None
            self.is_ready = False
            self.last_status = "Desconectado"

    def is_connected(self):
        return self.connection is not None and self.connection.is_connected()

    # ==========================================
    # PASSO 6: LOOP DE LEITURA (SIMPLIFICADO PARA TESTE)
    # ==========================================
    def _query(self, command):
        if not self.is_ready or not self.is_connected():
            return None
        try:
            response = self.connection.query(command)
            if not response.is_null():
                return response.value.magnitude
        except:
            pass
        return None

    def get_rpm(self): return self._query(obd.commands.RPM)
    def get_speed(self): return self._query(obd.commands.SPEED)
    def get_coolant_temp(self): return self._query(obd.commands.COOLANT_TEMP)
    def get_voltage(self):
        # Leitura de voltagem direta do ELM (independente do protocolo do carro)
        try:
            response = self.connection.query(obd.commands.ELM_VOLTAGE)
            return float(str(response.value).split('V')[0])
        except: return None