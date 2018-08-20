# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import network
from config import ESSID, PASSWORD

print("Starting...")


def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ESSID, PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ifconfig())

connect()

