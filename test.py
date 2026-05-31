import serial
import time

porta = "COM5"

try:

    ser = serial.Serial(
        porta,
        baudrate=38400,
        timeout=3
    )

    print("Porta aberta")

    comandos = [
        "ATZ",
        "ATI",
        "ATSP0"
    ]

    for cmd in comandos:

        print(f"\n>> {cmd}")

        ser.write((cmd + "\r").encode())

        time.sleep(1)

        resposta = ser.read_all()

        print(resposta.decode(errors="ignore"))

    ser.close()

except Exception as e:
    print("ERRO:", e)