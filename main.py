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
    # CONFIGURAÇÃO DA JANELA (MOBILE ADAPTIVE)
    # ==================================================

    page.title = "OBD Driver Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.adaptive = True
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10
    page.spacing = 10

    # Estado da aplicação
    obd = OBDManager()
    app_state = {
        "connected": False,
        "logging": False,
        "stream_running": False,
        "temperature_unit": "C"
    }

    os.makedirs("logs", exist_ok=True)

    # ==================================================
    # COMPONENTES DE INTERFACE (RESPONSIVOS)
    # ==================================================

    status_txt = ft.Text(
        "Desconectado",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED_400
    )

    perfil_dropdown = ft.Dropdown(
        label="Selecionar Perfil",
        expand=True,
        options=[ft.dropdown.Option(nome) for nome in VEHICLE_PROFILES.keys()]
    )

    # Campos de Info do Carro em modo Mobile
    modelo_input = ft.TextField(label="Modelo", expand=True, read_only=True)
    ano_input = ft.TextField(label="Ano", expand=True, read_only=True)
    motor_input = ft.TextField(label="Motor", expand=True, read_only=True)
    ecu_input = ft.TextField(label="ECU", expand=True, read_only=True)
    protocolo_dropdown = ft.Dropdown(
        label="Protocolo",
        expand=True,
        value="AUTO",
        options=[
            ft.dropdown.Option("AUTO"),
            ft.dropdown.Option("ISO9141"),
            ft.dropdown.Option("KWP2000"),
            ft.dropdown.Option("CAN"),
        ]
    )

    # No Android, list_ports não funciona bem. Usamos um TextField para MAC ou porta.
    porta_input = ft.TextField(
        label="Porta ou Endereço MAC Bluetooth",
        hint_text="PC: COMx | Android: 00:11:22:33:44:55",
        expand=True,
        value=""
    )

    # Sensores (Widgets)
    rpm_txt = ft.Text("0", size=32, weight="bold")
    speed_txt = ft.Text("0 km/h", size=32, weight="bold")
    temp_txt = ft.Text("0 °C", size=32, weight="bold")
    voltage_txt = ft.Text("0 V", size=32, weight="bold")

    dtc_list = ft.ListView(
        height=200,
        spacing=5,
        expand=True
    )

    # ==================================================
    # FUNÇÕES
    # ==================================================

    def carregar_perfil(e):
        perfil = perfil_dropdown.value
        if not perfil: return
        dados = VEHICLE_PROFILES[perfil]
        modelo_input.value = dados["modelo"]
        ano_input.value = dados["ano"]
        motor_input.value = dados["motor"]
        ecu_input.value = dados["ecu"]
        protocolo_dropdown.value = dados["protocolo"]
        page.update()

    async def conectar_obd(e):
        if not porta_input.value:
            status_txt.value = "Insira a porta ou MAC"
            status_txt.color = ft.Colors.RED_400
            page.update()
            return

        status_txt.value = "Conectando..."
        status_txt.color = ft.Colors.ORANGE_400
        page.update()

        try:
            sucesso = obd.connect(porta_input.value, protocolo_dropdown.value)
            if sucesso:
                app_state["connected"] = True
                status_txt.value = f"Conectado: {porta_input.value}"
                status_txt.color = ft.Colors.GREEN_400
                if not app_state["stream_running"]:
                    app_state["stream_running"] = True
                    page.run_task(atualizar_dashboard)
            else:
                status_txt.value = "Falha na conexão"
                status_txt.color = ft.Colors.RED_400
        except Exception as ex:
            status_txt.value = str(ex)
            status_txt.color = ft.Colors.RED_400
        page.update()

    def desconectar_obd(e):
        obd.disconnect()
        app_state["connected"] = False
        app_state["stream_running"] = False
        status_txt.value = "Desconectado"
        status_txt.color = ft.Colors.RED_400
        page.update()

    async def atualizar_dashboard():
        while app_state["connected"]:
            try:
                if not obd.is_connected():
                    status_txt.value = "Conexão perdida"
                    status_txt.color = ft.Colors.RED_400
                    page.update()
                    break

                rpm = obd.get_rpm()
                speed = obd.get_speed()
                temp = obd.get_coolant_temp()
                voltage = obd.get_voltage()

                if rpm is not None: rpm_txt.value = f"{int(rpm)}"
                if speed is not None: speed_txt.value = f"{int(speed)} km/h"
                if temp is not None: temp_txt.value = f"{int(temp)} °C"
                if voltage is not None: voltage_txt.value = f"{round(voltage,1)} V"

                page.update()
            except: pass
            await asyncio.sleep(0.5)

    def sensor_card(titulo, valor_widget):
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    [ft.Text(titulo, size=14), valor_widget],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

    # ==================================================
    # CONSTRUÇÃO DA PÁGINA
    # ==================================================

    page.add(
        ft.AppBar(
            title=ft.Text("OBD Driver Mobile"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            center_title=True,
            actions=[ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: page.update())]
        ),
        
        # Status Card
        ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Row([
                    ft.Icon(ft.Icons.BLUETOOTH, color=ft.Colors.BLUE_400),
                    status_txt
                ])
            )
        ),

        # Seção Perfil
        ft.ExpansionTile(
            title=ft.Text("Configuração do Veículo"),
            initially_expanded=True,
            controls=[
                ft.Padding(padding=10, content=ft.Column([
                    ft.Row([perfil_dropdown, ft.IconButton(ft.Icons.CHECK, on_click=carregar_perfil)]),
                    ft.Row([modelo_input, ano_input]),
                    ft.Row([motor_input, ecu_input]),
                    protocolo_dropdown
                ]))
            ]
        ),

        # Seção Conexão
        ft.ExpansionTile(
            title=ft.Text("Conexão Bluetooth"),
            initially_expanded=True,
            controls=[
                ft.Padding(padding=10, content=ft.Column([
                    porta_input,
                    ft.Row([
                        ft.FilledButton("Conectar", icon=ft.Icons.PLAY_ARROW, on_click=conectar_obd, expand=True),
                        ft.OutlinedButton("Sair", icon=ft.Icons.STOP, on_click=desconectar_obd, expand=True)
                    ])
                ]))
            ]
        ),

        # Dashboard Grid
        ft.Text("Monitoramento", size=18, weight="bold"),
        ft.ResponsiveRow([
            ft.Container(sensor_card("RPM", rpm_txt), col=6),
            ft.Container(sensor_card("Velocidade", speed_txt), col=6),
            ft.Container(sensor_card("Temperatura", temp_txt), col=6),
            ft.Container(sensor_card("Voltagem", voltage_txt), col=6),
        ]),

        # DTC Section
        ft.ExpansionTile(
            title=ft.Text("Diagnóstico (DTC)"),
            controls=[
                ft.Padding(padding=10, content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton("Ler Falhas", icon=ft.Icons.SEARCH, on_click=lambda e: page.update()),
                        ft.ElevatedButton("Limpar", icon=ft.Icons.DELETE_SWEEP, on_click=lambda e: page.update()),
                    ]),
                    dtc_list
                ]))
            ]
        )
    )

ft.app(target=main)