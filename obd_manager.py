import obd
import time

class OBDManager:
    def __init__(self):
        self.connection = None
        self.last_status = "Desconectado"

    # ==========================================
    # CONEXÃO
    # ==========================================
    def connect(self, port, protocolo="AUTO"):
        try:
            print(f"Tentando conectar em {port} com protocolo {protocolo}...")
            
            # Ajuste de baudrate comum para ELM327 Bluetooth/USB
            self.connection = obd.OBD(
                portstr=port,
                baudrate=38400,
                protocol=protocolo,
                timeout=15,
                fast=False
            )

            if self.connection.is_connected():
                self.last_status = f"Conectado: {self.connection.protocol_name()}"
                return True
            else:
                self.last_status = "Falha na conexão (Adaptador não responde)"
                return False

        except Exception as ex:
            self.last_status = f"Erro: {str(ex)}"
            print(f"Erro conexão: {ex}")
            return False

    # ==========================================
    # DESCONECTAR
    # ==========================================
    def disconnect(self):
        try:
            if self.connection:
                self.connection.close()
                print("Conexão OBD encerrada.")
        except Exception as ex:
            print(f"Erro ao desconectar: {ex}")
        finally:
            self.connection = None
            self.last_status = "Desconectado"

    # ==========================================
    # STATUS
    # ==========================================
    def is_connected(self):
        if not self.connection:
            return False
        return self.connection.is_connected()

    # ==========================================
    # CONSULTA GENÉRICA (ROBUSTEZ)
    # ==========================================
    def _query(self, command):
        if not self.is_connected():
            return None
        try:
            response = self.connection.query(command)
            if not response.is_null():
                return response.value.magnitude
        except Exception as ex:
            print(f"Erro na consulta {command}: {ex}")
        return None

    # ==========================================
    # SENSORES
    # ==========================================
    def get_rpm(self):
        return self._query(obd.commands.RPM)

    def get_speed(self):
        return self._query(obd.commands.SPEED)

    def get_coolant_temp(self):
        return self._query(obd.commands.COOLANT_TEMP)

    def get_voltage(self):
        # ELM_VOLTAGE retorna string ou valor dependendo da versão
        try:
            response = self.connection.query(obd.commands.ELM_VOLTAGE)
            if not response.is_null():
                # Tenta extrair apenas o número se vier com "V"
                val = str(response.value).replace("V", "").strip()
                return float(val)
        except:
            pass
        return None

    # ==========================================
    # DTC (FALHAS)
    # ==========================================
    def get_dtc(self):
        try:
            if not self.is_connected(): return []
            response = self.connection.query(obd.commands.GET_DTC)
            return response.value if response.value else []
        except:
            return []

    def clear_dtc(self):
        try:
            if not self.is_connected(): return False
            response = self.connection.query(obd.commands.CLEAR_DTC)
            return not response.is_null()
        except:
            return False