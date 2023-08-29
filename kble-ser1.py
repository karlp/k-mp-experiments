
import bluetooth
import aioble
import uasyncio as asyncio
from micropython import const

import tft_config

import vga1_16x16 as font


_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_GENERIC_THERMOMETER = const(768)

_ADV_INTERVAL_MS = const(250000)

temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_char = aioble.Characteristic(temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True)

k_service = aioble.Service(bluetooth.UUID("0c32766e-f93a-40bf-8b7a-8d5ba3b6114a"))
k_char_ctrl = aioble.Characteristic(k_service, bluetooth.UUID("90b996d6-8f71-4439-b80b-41d9e7edaccc"), read=True, write=True)
k_char_ctrl_ddesc = aioble.Descriptor(k_char_ctrl, bluetooth.UUID(0x2901), read=True)
k_char_ctrl_ddesc.write("my control char")
k_char_2 = aioble.Characteristic(k_service, bluetooth.UUID("ec4ad188-b475-4461-a910-ffa602a60139"), read=True, write=True)
k_char_2_ddesc = aioble.Descriptor(k_char_2, bluetooth.UUID(0x2901), read=True)
k_char_2_ddesc.write("my second char")


class KApp:
    def __init__(self):
        aioble.register_services(k_service, temp_service)
        self.tft = tft_config.config(rotation=3)
        self.tft.init()
        self.h = self.tft.height()
        self.w = self.tft.width()

    async def start(self, blah):
        self.tft.on()
        await asyncio.gather(
            self.t_periph(),
            self.t_screen_play(),
        )

    async def t_screen_play(self):
        self.tft.text(font, "hello", 0, 0)
        i = 0
        while True:
            await asyncio.sleep_ms(500)
            i += 1
            self.tft.text(font, f"hello {i}", 0, 0)

    async def handle_write_ctrl(self):
        while True:
            await k_char_ctrl.written()
            msg = k_char_ctrl.read()
            print(f"received ctrl write", msg)

    async def handle_write2(self):
        while True:
            await k_char_2.written()
            msg = k_char_2.read()
            print(f"received second write:", msg)
            # TODO - auto scroll text?! blah... screens are boring...
            self.tft.text(font, msg, 0, 20)

    # This is a single server object, I'd really like to make a multi conn one though really.
    async def t_periph(self):
        asyncio.create_task(self.handle_write_ctrl())
        asyncio.create_task(self.handle_write2())

        while True:
            async with await aioble.advertise(
                    _ADV_INTERVAL_MS,
                    name="temp-sense",
                    services=[_ENV_SENSE_UUID],
                    appearance=_GENERIC_THERMOMETER,
                    manufacturer=(0x999, b"1234"),
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
