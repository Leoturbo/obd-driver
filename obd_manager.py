import obd


class OBDManager:

    def __init__(self):

        self.connection = None

    # ==========================================
    # CONEXÃO
    # ==========================================

    def connect(
        self,
        port,
        protocolo="AUTO"
    ):

        try:

            self.connection = obd.OBD(
                portstr=port,
                baudrate=38400,
                protocol=protocolo,
                timeout=15,
                fast=False
            )

            return self.connection.is_connected()

        except Exception as ex:

            print("Erro conexão:", ex)
            return False

    # ==========================================
    # DESCONECTAR
    # ==========================================

    def disconnect(self):

        try:

            if self.connection:

                self.connection.close()

        except Exception as ex:

            print(ex)

        self.connection = None

    # ==========================================
    # STATUS
    # ==========================================

    def is_connected(self):

        if not self.connection:
            return False

        try:
            return self.connection.is_connected()

        except:
            return False

    # ==========================================
    # RPM
    # ==========================================

    def get_rpm(self):

        try:

            response = self.connection.query(
                obd.commands.RPM
            )

            if response.value:

                return float(
                    response.value.magnitude
                )

        except:
            pass

        return None

    # ==========================================
    # VELOCIDADE
    # ==========================================

    def get_speed(self):

        try:

            response = self.connection.query(
                obd.commands.SPEED
            )

            if response.value:

                return float(
                    response.value.magnitude
                )

        except:
            pass

        return None

    # ==========================================
    # TEMPERATURA
    # ==========================================

    def get_coolant_temp(self):

        try:

            response = self.connection.query(
                obd.commands.COOLANT_TEMP
            )

            if response.value:

                return float(
                    response.value.magnitude
                )

        except:
            pass

        return None

    # ==========================================
    # VOLTAGEM ECU
    # ==========================================

    def get_voltage(self):

        try:

            response = self.connection.query(
                obd.commands.ELM_VOLTAGE
            )

            if response.value:

                return float(
                    response.value.magnitude
                )

        except:
            pass

        return None

    # ==========================================
    # DTC
    # ==========================================

    def get_dtc(self):

        try:

            response = self.connection.query(
                obd.commands.GET_DTC
            )

            if response.value:

                return response.value

        except:
            pass

        return []

    # ==========================================
    # LIMPAR DTC
    # ==========================================

    def clear_dtc(self):

        try:

            response = self.connection.query(
                obd.commands.CLEAR_DTC
            )

            return response is not None

        except:
            return False

    # ==========================================
    # INFO
    # ==========================================

    def get_protocol(self):

        try:

            return self.connection.protocol_name()

        except:

            return "Desconhecido"