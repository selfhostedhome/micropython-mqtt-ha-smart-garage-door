from umqtt.simple import MQTTClient
from switch import Switch
import machine
import ubinascii
import time

from config import SERVER, COMMAND_TOPIC, STATE_TOPIC, AVAILABILITY_TOPIC

CLIENT = None
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

relay_pin = None


def new_msg(topic, msg):
    print("Received {} on {} topic".format(msg, topic))
    print("Turning relay on")
    relay_pin.value(1)
    time.sleep_ms(600)
    print("Turning relay off")
    relay_pin.value(0)


def main():
    global relay_pin

    client = MQTTClient(CLIENT_ID, SERVER)
    client.set_callback(new_msg)

    try:
        client.connect()
    except OSError:
        print("MQTT Broker seems down")
        print("Resetting after 20 seconds")
        time.sleep(20)
        machine.reset()

    client.subscribe(COMMAND_TOPIC)

    # Publish as available once connected
    client.publish(AVAILABILITY_TOPIC, "online", retain=True)

    switch_pin = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
    reed_switch = Switch(switch_pin)

    # Initialize state of garage door after booting up
    if switch_pin.value():
        client.publish(STATE_TOPIC, "open")
    else:
        client.publish(STATE_TOPIC, "closed")

    relay_pin = machine.Pin(4, machine.Pin.OUT, 0)

    try:
        while True:

            reed_switch_new_value = False

            # Disable interrupts for a short time to read shared variable
            irq_state = machine.disable_irq()
            if reed_switch.new_value_available:
                reed_switch_value = reed_switch.value
                reed_switch_new_value = True
                reed_switch.new_value_available = False
            machine.enable_irq(irq_state)

            # If the reed switch had a new value, publish the new state
            if reed_switch_new_value:
                if reed_switch_value:
                    client.publish(STATE_TOPIC, "open")
                else:
                    client.publish(STATE_TOPIC, "closed")

            # Process any MQTT messages
            if client.check_msg():
                client.wait_msg()

    finally:
        client.publish(AVAILABILITY_TOPIC, "offline", retain=False)
        client.disconnect()
        machine.reset()


main()

# Should never leave main() function, but if program crashes reset
machine.reset()
