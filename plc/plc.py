from __future__ import annotations

from pycomm3 import LogixDriver

IP = "192.168.1.10"


def read_tags(tag_name: str):
    try:
        with LogixDriver(IP) as plc:
            return plc.read(tag_name).value
    except Exception as e:
        print(f"{e} - Error on plc communication")
        return e


def write_tag(tag_name: str, value: str | int | float | bool):
    try:
        with LogixDriver(IP) as plc:
            plc.write((tag_name, value))
    except Exception as e:
        print(f"{e} - Error on plc communication")
        return e


def read_multiples(tag_list):
    try:
        with LogixDriver(IP) as plc:
            return plc.read(*tag_list)
    except Exception as e:
        print(f"{e} - Error on plc communication")
        return e
