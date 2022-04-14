import array
import usb.core

device = usb.core.find(idVendor=0x16C0, idProduct=0x05DF)
_pass = False

def set_report(data):
    global device, _pass
    try:
        if not device:
            device = usb.core.find(idVendor=0x16C0, idProduct=0x05DF)
        ret = device.ctrl_transfer(
            0x20,
            0x9,
            (3 << 8),
            0,
            data,
            5000
        )
        _pass = False
        return ret
    except AttributeError as e:
        if not _pass:
            print(f"{e} - set_report - ctrl_relay.py")
            _pass = True
    except Exception as e:
        device = None
        print(f"{e} - set_report - ctrl_relay.py")


def turn_on():
    buf = array.array("B")
    buf.append(0xFE)
    for i in range(0, 7):
        buf.append(0x00)
    set_report(buf)


def turn_off():
    buf = array.array("B")
    buf.append(0xFC)
    for i in range(0, 7):
        buf.append(0x00)
    set_report(buf)
