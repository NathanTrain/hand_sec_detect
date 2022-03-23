"""
Relay controlling

Usa a porta serial especifica para conectar ao relé e escreve, usando bytes.

-> All on it wrote "FF FF"
-> All off it wrote "00 00"

-> Relay 1 on "01 01"
-> Relay 1 and Relay 2 on "03 03"
-> Relay 1 off and Relay 2 on "02 02"
-> Relay 2 and Relay 4 on "0A 0A"
"""

import time
import serial

try:
    s = serial.Serial(port="COM4", baudrate=9600, bytesize=serial.EIGHTBITS,
                      parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)

    while True:
        if s.isOpen():
            s.write([b"\00", b"\00"])
            time.sleep(1)
            s.write([b"\xFF", b"\xFF"])
            time.sleep(1)
        else:
            s.open()
except Exception as e:
    print(e)
