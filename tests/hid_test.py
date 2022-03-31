import time

import pyhid_usb_relay as pyhid

def enable_relay():
    usb_relay = pyhid.find()
    usb_relay.set_state("all", True)
    time.sleep(0.05)


def disable_relay():
    usb_relay = pyhid.find()
    usb_relay.set_state("all", False)
    time.sleep(0.05)

