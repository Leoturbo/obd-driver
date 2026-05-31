import flet as ft
import asyncio
import csv
import os

from datetime import datetime

import serial.tools.list_ports

from obd_manager import OBDManager
from vehicle_profiles import VEHICLE_PROFILES


def main(page: ft.Page):

    # ==================================================
    # CONFIGURAÇÃO DA JANELA
    # ==================================================

    page.title = "OBD Driver MVP"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1400
    page.window_height = 900
    page.scroll = ft.ScrollMode.AUTO

    page.padding = 20
    page.spacing = 15

    # ==================================================
    # ESTADO DA APLICAÇÃO
    # ==================================================

    obd = OBDManager()

    app_state = {
        "connected": False,
        "logging": False,
        "stream_running": False,
        "temperature_unit": "C"
    }

    # ==================================================
    # PASTAS
    # ==================================================

    os.makedirs("logs", exist_ok=True)

    # ==================================================
    # STATUS
    # ==================================================

    status_txt = ft.Text(
        "Desconectado",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED_400
    )

    # ==================================================
    # PERFIL DO VEÍCULO
    # ==================================================

    perfil_dropdown = ft.Dropdown(
        label="Perfil do Veículo",
        width=450,
        options=[
            ft.dropdown.Option(nome)
            for nome in VEHICLE_PROFILES.keys()
        ]
    )

    modelo_input = ft.TextField(
        label="Modelo",
        width=180
    )

    ano_input = ft.TextField(
        label="Ano",
        width=120
    )

    motor_input = ft.TextField(
        label="Motor",
        width=180
    )

    ecu_input = ft.TextField(
        label="ECU",
        width=220
    )

    protocolo_dropdown = ft.Dropdown(
        label="Protocolo",

        width=180,

        value="AUTO",

        options=[
            ft.dropdown.Option("AUTO"),
            ft.dropdown.Option("ISO9141"),
            ft.dropdown.Option("KWP2000"),
            ft.dropdown.Option("KW81"),
            ft.dropdown.Option("KW82"),
            ft.dropdown.Option("ALDL160"),
            ft.dropdown.Option("ALDL8192")
        ]
    )

    # ==================================================
    # PORTA COM
    # ==================================================

    porta_dropdown = ft.Dropdown(
        label="Porta COM",
        width=350
    )

    # ==================================================
    # SENSORES
    # ==================================================

    rpm_txt = ft.Text(
        "0",
        size=34,
        weight=ft.FontWeight.BOLD
    )

    speed_txt = ft.Text(
        "0 km/h",
        size=34,
        weight=ft.FontWeight.BOLD
    )

    temp_txt = ft.Text(
        "0 °C",
        size=34,
        weight=ft.FontWeight.BOLD
    )

    voltage_txt = ft.Text(
        "0 V",
        size=34,
        weight=ft.FontWeight.BOLD
    )

    # ==================================================
    # LISTA DE FALHAS
    # ==================================================

    dtc_list = ft.ListView(
        height=250,
        spacing=5,
        expand=True
    )

    # ==================================================
    # FUNÇÕES DE INTERFACE
    # ==================================================

    def carregar_perfil(e):

        perfil = perfil_dropdown.value

        if not perfil:
            return

        dados = VEHICLE_PROFILES[perfil]

        modelo_input.value = dados["modelo"]
        ano_input.value = dados["ano"]
        motor_input.value = dados["motor"]
        ecu_input.value = dados["ecu"]
        protocolo_dropdown.value = dados["protocolo"]

        page.update()

    # ==================================================
    # LISTAR PORTAS COM
    # ==================================================

    def atualizar_portas(e=None):

        porta_dropdown.options.clear()

        try:

            portas = serial.tools.list_ports.comports()

            for porta in portas:

                porta_dropdown.options.append(
                    ft.dropdown.Option(
                        key=porta.device,
                        text=f"{porta.device} - {porta.description}"
                    )
                )

        except Exception as ex:

            print(ex)

        page.update()

    # ==================================================
    # CARD SENSOR
    # ==================================================

    def sensor_card(
        titulo,
        valor_widget
    ):

        return ft.Card(
            elevation=8,
            content=ft.Container(
                padding=20,
                border_radius=15,
                content=ft.Column(
                    [
                        ft.Text(
                            titulo,
                            size=16,
                            weight=ft.FontWeight.W_500
                        ),

                        valor_widget
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

    # ==================================================
    # BOTÕES
    # ==================================================

    carregar_perfil_btn = ft.FilledButton(
        content=ft.Text("Carregar Perfil"),
        icon=ft.Icons.DIRECTIONS_CAR,
        on_click=carregar_perfil
    )

    atualizar_com_btn = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Atualizar Portas COM",
        on_click=atualizar_portas
    )

    connect_btn = ft.FilledButton(
        content=ft.Text("Conectar"),
        icon=ft.Icons.BLUETOOTH_CONNECTED
    )

    disconnect_btn = ft.OutlinedButton(
        content=ft.Text("Desconectar"),
        icon=ft.Icons.BLUETOOTH_DISABLED
    )

    log_btn = ft.FilledButton(
        content=ft.Text("Iniciar Log"),
        icon=ft.Icons.SAVE
    )

    scan_btn = ft.FilledButton(
        content=ft.Text("Ler Falhas"),
        icon=ft.Icons.SEARCH
    )

    clear_btn = ft.FilledButton(
        content=ft.Text("Apagar Falhas"),
        icon=ft.Icons.DELETE
    )

    # ==================================================
    # DASHBOARD
    # ==================================================

    dashboard = ft.ResponsiveRow(
        controls=[

            ft.Container(
                sensor_card(
                    "RPM",
                    rpm_txt
                ),
                col={
                    "sm": 6,
                    "md": 3
                }
            ),

            ft.Container(
                sensor_card(
                    "Velocidade",
                    speed_txt
                ),
                col={
                    "sm": 6,
                    "md": 3
                }
            ),

            ft.Container(
                sensor_card(
                    "Temperatura",
                    temp_txt
                ),
                col={
                    "sm": 6,
                    "md": 3
                }
            ),

            ft.Container(
                sensor_card(
                    "Voltagem ECU",
                    voltage_txt
                ),
                col={
                    "sm": 6,
                    "md": 3
                }
            )

        ]
    )

    # ==================================================
    # CARREGAR PORTAS AO INICIAR
    # ==================================================

    atualizar_portas()


    # ==================================================
    # CONECTAR ELM327
    # ==================================================

    async def conectar_obd(e):

        if not porta_dropdown.value:

            status_txt.value = "Selecione uma porta COM"
            status_txt.color = ft.Colors.RED_400

            page.update()
            return

        status_txt.value = "Conectando..."
        status_txt.color = ft.Colors.ORANGE_400

        page.update()

        try:

            sucesso = obd.connect(
                porta_dropdown.value,
                protocolo_dropdown.value
            )

            if sucesso:

                app_state["connected"] = True

                status_txt.value = (
                    f"Conectado em {porta_dropdown.value}"
                )

                status_txt.color = ft.Colors.GREEN_400

                if not app_state["stream_running"]:

                    app_state["stream_running"] = True

                    page.run_task(
                        atualizar_dashboard
                    )

            else:

                status_txt.value = (
                    "Falha na conexão"
                )

                status_txt.color = ft.Colors.RED_400

        except Exception as ex:

            status_txt.value = str(ex)

            status_txt.color = ft.Colors.RED_400

        page.update()

    # ==================================================
    # DESCONECTAR
    # ==================================================

    def desconectar_obd(e):

        obd.disconnect()

        app_state["connected"] = False
        app_state["stream_running"] = False

        status_txt.value = "Desconectado"
        status_txt.color = ft.Colors.RED_400

        page.update()

    # ==================================================
    # STREAM TEMPO REAL
    # ==================================================

    async def atualizar_dashboard():

        while app_state["connected"]:

            try:

                if not obd.is_connected():

                    status_txt.value = (
                        "Conexão perdida"
                    )

                    status_txt.color = ft.Colors.RED_400

                    page.update()

                    break

                rpm = obd.get_rpm()

                speed = obd.get_speed()

                temp = obd.get_coolant_temp()

                voltage = obd.get_voltage()

                # RPM

                if rpm is not None:

                    rpm_txt.value = (
                        f"{int(rpm)}"
                    )

                # VELOCIDADE

                if speed is not None:

                    speed_txt.value = (
                        f"{int(speed)} km/h"
                    )

                # TEMPERATURA

                if temp is not None:

                    temp_txt.value = (
                        f"{int(temp)} °C"
                    )

                # VOLTAGEM

                if voltage is not None:

                    voltage_txt.value = (
                        f"{round(voltage,1)} V"
                    )

                # LOG CSV

                if app_state["logging"]:

                    gravar_csv(
                        rpm,
                        speed,
                        temp,
                        voltage
                    )

                page.update()

            except Exception as ex:

                print(
                    "Erro stream:",
                    ex
                )

            await asyncio.sleep(0.5)

        app_state["stream_running"] = False

    # ==================================================
    # EVENTOS DOS BOTÕES
    # ==================================================

    connect_btn.on_click = conectar_obd

    disconnect_btn.on_click = desconectar_obd

        # ==================================================
    # CSV
    # ==================================================

    def gravar_csv(
        rpm,
        speed,
        temp,
        voltage
    ):

        arquivo = "logs/obd_log.csv"

        existe = os.path.exists(
            arquivo
        )

        with open(
            arquivo,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            if not existe:

                writer.writerow([
                    "timestamp",
                    "rpm",
                    "speed",
                    "temperature",
                    "voltage"
                ])

            writer.writerow([
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                rpm,
                speed,
                temp,
                voltage
            ])

    # ==================================================
    # LOG ON/OFF
    # ==================================================

    def alternar_log(e):

        app_state["logging"] = (
            not app_state["logging"]
        )

        if app_state["logging"]:

            log_btn.text = "Parar Log"

            status_txt.value = (
                "Gravando CSV..."
            )

        else:

            log_btn.text = "Iniciar Log"

            status_txt.value = (
                "Log parado"
            )

        page.update()

    log_btn.on_click = alternar_log

    # ==================================================
    # LEITURA DE FALHAS
    # ==================================================

    def ler_falhas(e):

        dtc_list.controls.clear()

        if not obd.is_connected():

            dtc_list.controls.append(
                ft.Text(
                    "Veículo não conectado",
                    color=ft.Colors.RED_400
                )
            )

            page.update()
            return

        try:

            erros = obd.get_dtc()

            if not erros:

                dtc_list.controls.append(
                    ft.Text(
                        "Nenhuma falha encontrada",
                        color=ft.Colors.GREEN_400
                    )
                )

            else:

                for codigo, descricao in erros:

                    dtc_list.controls.append(

                        ft.Card(
                            content=ft.Container(
                                padding=10,
                                content=ft.Column([

                                    ft.Text(
                                        codigo,
                                        size=18,
                                        weight=ft.FontWeight.BOLD
                                    ),

                                    ft.Text(
                                        descricao
                                    )

                                ])
                            )
                        )

                    )

        except Exception as ex:

            dtc_list.controls.append(
                ft.Text(
                    str(ex),
                    color=ft.Colors.RED_400
                )
            )

        page.update()

    # ==================================================
    # LIMPAR FALHAS
    # ==================================================

    def limpar_falhas(e):

        if not obd.is_connected():

            return

        try:

            sucesso = obd.clear_dtc()

            dtc_list.controls.clear()

            if sucesso:

                dtc_list.controls.append(
                    ft.Text(
                        "Falhas apagadas com sucesso",
                        color=ft.Colors.GREEN_400
                    )
                )

            else:

                dtc_list.controls.append(
                    ft.Text(
                        "Falha ao limpar DTC",
                        color=ft.Colors.RED_400
                    )
                )

        except Exception as ex:

            dtc_list.controls.append(
                ft.Text(
                    str(ex),
                    color=ft.Colors.RED_400
                )
            )

        page.update()

    scan_btn.on_click = ler_falhas

    clear_btn.on_click = limpar_falhas

        # ==================================================
    # CABEÇALHO
    # ==================================================

    header = ft.Container(
        padding=15,
        border_radius=15,
        bgcolor=ft.Colors.BLUE_GREY_900,
        content=ft.Row(
            [
                ft.Icon(
                    ft.Icons.DIRECTIONS_CAR,
                    size=40
                ),

                ft.Column(
                    [
                        ft.Text(
                            "OBD DRIVER MVP",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),

                        status_txt
                    ],
                    spacing=5
                )
            ]
        )
    )

    # ==================================================
    # PERFIL VEÍCULO
    # ==================================================

    perfil_section = ft.Container(
        padding=15,
        border_radius=15,
        bgcolor=ft.Colors.BLACK12,
        content=ft.Column(
            [
                ft.Text(
                    "Perfil do Veículo",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Row([
                    perfil_dropdown,
                    carregar_perfil_btn
                ]),

                ft.ResponsiveRow([

                    ft.Container(
                        modelo_input,
                        col={"sm": 6, "md": 2}
                    ),

                    ft.Container(
                        ano_input,
                        col={"sm": 6, "md": 2}
                    ),

                    ft.Container(
                        motor_input,
                        col={"sm": 6, "md": 2}
                    ),

                    ft.Container(
                        ecu_input,
                        col={"sm": 6, "md": 3}
                    ),

                    ft.Container(
                        protocolo_dropdown,
                        col={"sm": 6, "md": 3}
                    )

                ])
            ]
        )
    )

    # ==================================================
    # CONEXÃO
    # ==================================================

    conexao_section = ft.Container(
        padding=15,
        border_radius=15,
        bgcolor=ft.Colors.BLACK12,
        content=ft.Column(
            [
                ft.Text(
                    "Conexão Bluetooth / ELM327",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Row(
                    [
                        porta_dropdown,
                        atualizar_com_btn,
                        connect_btn,
                        disconnect_btn
                    ]
                )
            ]
        )
    )

    # ==================================================
    # DASHBOARD
    # ==================================================

    dashboard_section = ft.Container(
        padding=15,
        border_radius=15,
        bgcolor=ft.Colors.BLACK12,
        content=ft.Column(
            [
                ft.Text(
                    "Monitoramento em Tempo Real",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                dashboard
            ]
        )
    )

    # ==================================================
    # LOG CSV
    # ==================================================

    log_section = ft.Container(
        padding=15,
        border_radius=15,
        bgcolor=ft.Colors.BLACK12,
        content=ft.Column(
            [
                ft.Text(
                    "Data Logger",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                log_btn
            ]
        )
    )

    # ==================================================
    # DTC
    # ==================================================

    dtc_section = ft.Container(
        padding=15,
        border_radius=15,
        bgcolor=ft.Colors.BLACK12,
        content=ft.Column(
            [
                ft.Text(
                    "Diagnóstico de Falhas",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Row(
                    [
                        scan_btn,
                        clear_btn
                    ]
                ),

                dtc_list
            ]
        )
    )

    # ==================================================
    # RODAPÉ
    # ==================================================

    footer = ft.Container(
        alignment=ft.alignment.center if hasattr(ft.alignment, "center") else None,
        padding=20,
        content=ft.Text(
            "OBD Driver MVP • ELM327 Bluetooth • GM Astra / Zafira / Corsa / Vectra",
            size=12,
            color=ft.Colors.GREY_500
        )
    )

    # ==================================================
    # PAGE ADD
    # ==================================================

    page.add(
        header,
        perfil_section,
        conexao_section,
        dashboard_section,
        log_section,
        dtc_section,
        footer
    )


# ==================================================
# START APP
# ==================================================

ft.app(target=main)    