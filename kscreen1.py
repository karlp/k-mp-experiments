# ESP32 Example
# To use baudrates above 26.6MHz you must use my firmware or modify the micropython
# source code to increase the SPI baudrate limit by adding SPI_DEVICE_NO_DUMMY to the
# .flag member of the spi_device_interface_config_t struct in the machine_hw_spi_init_internal.c
# file.  Not doing so will cause the ESP32 to crash if you use a baudrate that is too high.

import machine
import st7789
# For a Lilygo TTGO T-Display
# 20MHz is enough, 
spi = machine.SPI(2, baudrate=26000000, polarity=1, sck=machine.Pin(18), mosi=machine.Pin(19))
display = st7789.ST7789(spi, 135, 240,
        #reset=None,
        dc=machine.Pin(16, machine.Pin.OUT),
        cs=machine.Pin(5, machine.Pin.OUT),
        backlight=machine.Pin(4, machine.Pin.OUT)
        )
display.init()
#display.on()

