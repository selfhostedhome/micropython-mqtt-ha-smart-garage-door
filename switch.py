import machine

class Switch():
    def __init__(self, pin):
        self.pin = pin
        self.pin.irq(handler=self.switch_change,
                     trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING)

        self.debounce_timer = machine.Timer(-1)
        self.new_value_available = False
        self.value = None
        self.prev_value = None
        self.debounce_checks = 0

    def switch_change(self, pin):
        self.value = pin.value()

        # Start timer to check for debounce
        self.debounce_checks = 0
        self.start_debounce_timer()

        # Disable IRQs for GPIO pin while debouncing
        self.pin.irq(trigger=0)

    def start_debounce_timer(self):
        self.debounce_timer.init(period=100, mode=machine.Timer.ONE_SHOT,
                                 callback=self.check_debounce)

    def check_debounce(self, _):
        new_value = self.pin.value()

        if new_value == self.value:
            self.debounce_checks = self.debounce_checks + 1

            if self.debounce_checks == 3:
                # Values are the same, debouncing done

                # Check if this is actually a new value for the application
                if self.prev_value != self.value:
                    self.new_value_available = True
                    self.prev_value = self.value

                # Re-enable the Switch IRQ to get the next change
                self.pin.irq(handler=self.switch_change,
                             trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING)
            else:
                # Start the timer over to make sure debounce value stays the same
                self.start_debounce_timer()
        else:
            # Values are not the same, update value we're checking for and
            # delay again
            self.debounce_checks = 0
            self.value = new_value
            self.start_debounce_timer()

