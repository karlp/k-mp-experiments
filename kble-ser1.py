
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

aioble.register_services(temp_service)
aioble.register_services(k_service)

lolq = []

async def handle_write_ctrl(dat):
    while True:
        await k_char_ctrl.written()
        msg = k_char_ctrl.read()
        print(f"received ctrl write", msg)


async def handle_write2(dat):
    while True:
        await k_char_2.written()
        msg = k_char_2.read()
        print(f"received second write:", msg)


# This is a single server object, I'd really like to make a multi conn one though really.
async def k_periph_task():
    asyncio.create_task(handle_write_ctrl("blah"))
    asyncio.create_task(handle_write2("wop"))

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


async def t_screen_play():
    tft = tft_config.config(rotation=3)
    tft.init()
    tft.on()
    h = tft.height()
    w = tft.width()

    tft.text(font, "hello", 0, 0)

    i = 0
    while True:
        await asyncio.sleep_ms(500)
        i += 1
        tft.text(font, f"hello {i}", 0, 0)





# Run both tasks.
async def main():
    print("starting...")
    await asyncio.gather(
        k_periph_task(),
        t_screen_play(),
        )
    print("never hit here")



asyncio.run(main())