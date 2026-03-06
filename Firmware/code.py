import board
import busio
import supervisor
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners.keypad import KeysScanner
from kmk.modules.encoder import EncoderHandler
from kmk.modules.macros import Macros, Press, Release, Tap, Delay
from kmk.extensions.media_keys import MediaKeys

# OLED
displayio.release_displays()
i2c = busio.I2C(scl=board.D5, sda=board.D4)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

splash = displayio.Group()
display.show(splash)
oled_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=4, y=14)
splash.append(oled_label)

_oled_clear_at = None

def oled_show(msg, timeout_ms=3000):
    global _oled_clear_at
    oled_label.text = msg
    _oled_clear_at = supervisor.ticks_ms() + timeout_ms

# Keyboard
keyboard = KMKKeyboard()
keyboard.extensions.append(MediaKeys())

macros = Macros()
keyboard.modules.append(macros)

keyboard.matrix = KeysScanner(
    pins=[
        board.D7,   # SW1 -> MUTE
        board.D8,   # SW2 -> PLAY/PAUSE
        board.D9,   # SW3 -> NEXT TRACK
        board.D10,  # SW4 -> PRINT SCREEN
        board.D3,   # SW5 -> WORKFLOW
        board.D6,   # SW6 -> CLOSE ALL
    ],
    value_when_pressed=False,
    pull=True,
)

# Macros
# WORKFLOW: open VSCode + 4 Firefox tabs via Win+R
WORKFLOW = KC.MACRO(
    Press(KC.LGUI), Tap(KC.R), Release(KC.LGUI),
    Delay(300),
    "code\n",
    Delay(1000),

    Press(KC.LGUI), Tap(KC.R), Release(KC.LGUI),
    Delay(300),
    "start firefox https://classroom.google.com\n",
    Delay(500),

    Press(KC.LGUI), Tap(KC.R), Release(KC.LGUI),
    Delay(300),
    "start firefox https://mail.google.com\n",
    Delay(500),

    Press(KC.LGUI), Tap(KC.R), Release(KC.LGUI),
    Delay(300),
    "start firefox https://youtube.com\n",
    Delay(500),

    Press(KC.LGUI), Tap(KC.R), Release(KC.LGUI),
    Delay(300),
    "start firefox https://pomofocus.io/\n",
)

# CLOSE_ALL: Alt+F4 ten times
CLOSE_ALL = KC.MACRO(
    *[step
      for _ in range(10)
      for step in (Press(KC.LALT), Tap(KC.F4), Release(KC.LALT), Delay(250))]
)

# Keymap
keyboard.keymap = [
    [
        KC.MUTE,  KC.MPLY,   KC.MNXT,
        KC.PSCR,  WORKFLOW,  CLOSE_ALL,
    ]
]

# Encoder
encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)
encoder_handler.pins = ((board.D0, board.D1, None, False),)
encoder_handler.map = [((KC.VOLD, KC.VOLU),)]

# OLED
_KEY_LABELS = {
    KC.MUTE:   "Mute",
    KC.MPLY:   "Play/Pause",
    KC.MNXT:   "Next Track",
    KC.PSCR:   "Print Screen",
    WORKFLOW:  "Workflow",
    CLOSE_ALL: "Close All",
}

class OledExtension:
    def during_bootup(self, keyboard):
        oled_show("Ready!", timeout_ms=2000)

    def before_matrix_scan(self, keyboard):
        global _oled_clear_at
        if _oled_clear_at and supervisor.ticks_ms() >= _oled_clear_at:
            oled_label.text = ""
            _oled_clear_at = None

    def after_matrix_scan(self, keyboard): pass

    def before_hid_send(self, keyboard):
        for key in keyboard.keys_pressed:
            msg = _KEY_LABELS.get(key)
            if msg:
                oled_show(msg)
                return

    def after_hid_send(self, keyboard): pass
    def on_powersave_enable(self, keyboard): pass
    def on_powersave_disable(self, keyboard): pass

keyboard.extensions.append(OledExtension())

_orig_move = EncoderHandler.on_move_do

def _enc_move(self, keyboard, state, direction):
    oled_show("Vol Up" if direction > 0 else "Vol Down")
    _orig_move(self, keyboard, state, direction)

EncoderHandler.on_move_do = _enc_move


if __name__ == "__main__":
    keyboard.go()
