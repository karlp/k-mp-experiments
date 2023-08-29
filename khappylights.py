#!/usr/bin/env python
"""
Attempt to emulate Trione / Happy Lighting bluetooth RGB led controller

See: https://github.com/madhead/saberlight/blob/master/protocols/Triones/protocol.md
and similar
"""
import bluetooth
import aioble
import uasyncio as asyncio
from micropython import const

#import tft_config

#import vga1_16x16 as font

_original = """
svc handle: 10 uuid: 0000ffd0-0000-1000-8000-00805f9b34fb, desc: Vendor specific
     char: 11 uuid: 0000ffd4-0000-1000-8000-00805f9b34fb desc: Vendor specific 
     char: 14 uuid: 0000ffd1-0000-1000-8000-00805f9b34fb desc: Vendor specific 
svc handle: 4 uuid: 0000ffd5-0000-1000-8000-00805f9b34fb, desc: Vendor specific
     char: 5 uuid: 0000ffda-0000-1000-8000-00805f9b34fb desc: Vendor specific 
     char: 8 uuid: 0000ffd9-0000-1000-8000-00805f9b34fb desc: Vendor specific 
"""

_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_GENERIC_THERMOMETER = const(768)

_ADV_INTERVAL_MS = const(250000)

SVC_A = aioble.Service(bluetooth.UUID(0xffd5))
C_CTRL = aioble.Characteristic(SVC_A, bluetooth.UUID(0xffd9), write=True, write_no_response=True)
_C_CTRL_A = aioble.Characteristic(SVC_A, bluetooth.UUID(0xffda), notify=True)  # purpose unknown
SVC_B = aioble.Service(bluetooth.UUID(0xffd0))
C_CTRL_NOT = aioble.Characteristic(SVC_B, bluetooth.UUID(0xffd4), notify=True)
_C_UNKNOWN = aioble.Characteristic(SVC_B, bluetooth.UUID(0xffd1), write_no_response=True)  # purpose unknown

class KApp:
    def __init__(self):
        aioble.register_services(SVC_A, SVC_B)
        # self.tft = tft_config.config(rotation=3)
        # self.tft.init()
        # self.h = self.tft.height()
        # self.w = self.tft.width()

    async def start(self, blah):
        # self.tft.on()
        await asyncio.gather(
            self.t_periph(),
            # self.t_screen_play(),
        )

    # async def t_screen_play(self):
    #     self.tft.text(font, "hello", 0, 0)
    #     i = 0
    #     while True:
    #         await asyncio.sleep_ms(500)
    #         i += 1
    #         self.tft.text(font, f"hello {i}", 0, 0)

    async def handle_write_ctrl(self):
        while True:
            await C_CTRL.written()
            msg = C_CTRL.read()
            print(f"received ctrl write", msg)

    # async def handle_write2(self):
    #     while True:
    #         await k_char_2.written()
    #         msg = k_char_2.read()
    #         print(f"received second write:", msg)
    #         # TODO - auto scroll text?! blah... screens are boring...
    #         self.tft.text(font, msg, 0, 20)

    # This is a single server object, I'd really like to make a multi conn one though really.
    async def t_periph(self):
        asyncio.create_task(self.handle_write_ctrl())
        #asyncio.create_task(self.handle_write2())

        while True:
            async with await aioble.advertise(
                    _ADV_INTERVAL_MS,
                    name="QHM-4242",
                    #services=[_ENV_SENSE_UUID],
                    #appearance=_GENERIC_THERMOMETER,
                    #manufacturer=(0x999, b"1234"),
            ) as connection:
                print("Connection from", connection.device)
                #await asyncio.create_task(t_handle_client(connection))
                #await t_handle_client(connection)
                await connection.disconnected()
                print("disconnected, advertising again...")


# Boilerplate below here ##########
def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


async def main():
    print("starting...")
    set_global_exception()  # Debug aid
    app = KApp()
    await app.start("adsf")
    print("never hit here")


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state
