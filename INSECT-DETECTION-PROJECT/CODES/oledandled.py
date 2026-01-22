import lgpio
import board
import busio
from PIL import Image, ImageDraw, ImageFont

try:
    import adafruit_ssd1306
    OLED_AVAILABLE = True
except ImportError:
    print("⚠️ adafruit_ssd1306 not found, OLED disabled.")
    OLED_AVAILABLE = False

# LED pins
RED_LED = 17
YELLOW_LED = 27
GREEN_LED = 22

# Open GPIO chip safely
try:
    chip = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(chip, RED_LED)
    lgpio.gpio_claim_output(chip, YELLOW_LED)
    lgpio.gpio_claim_output(chip, GREEN_LED)
except lgpio.error as e:
    print(f"⚠️ GPIO busy or error: {e}")
    chip = None

def reset_leds():
    if chip:
        lgpio.gpio_write(chip, RED_LED, 0)
        lgpio.gpio_write(chip, YELLOW_LED, 0)
        lgpio.gpio_write(chip, GREEN_LED, 0)

# OLED setup
oled = None
if OLED_AVAILABLE:
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        oled.fill(0)
        oled.show()
    except Exception as e:
        print(f"⚠️ OLED not found or I2C error: {e}")
        oled = None

def display_on_oled(lines):
    if oled:
        oled.fill(0)
        oled.show()
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        for i, line in enumerate(lines[:5]):
            draw.text((0, i * 12), line, font=font, fill=255)
        oled.image(image)
        oled.show()
    else:
        print("OLED disabled, cannot display:", lines)

def cleanup():
    reset_leds()
    if chip:
        lgpio.gpiochip_close(chip)
    if oled:
        oled.fill(0)
        oled.show()
