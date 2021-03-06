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
    s = serial.Serial(port="COM1", baudrate=9600, bytesize=serial.EIGHTBITS,
                      parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)

    while True:
        if s.isOpen():
            print(s.read())
        else:
            raise Exception("Port not opened")
except Exception as e:
    print(e)
