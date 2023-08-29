import micropython_dotstar
import machine

# t-embed apa102 clk = 45, di = 42 (44 is an unused pin on the grove connector)
spi = machine.SPI(sck=machine.Pin(45), mosi=machine.Pin(42), miso=machine.Pin(37))
dots = micropython_dotstar.DotStar(spi, 7)

