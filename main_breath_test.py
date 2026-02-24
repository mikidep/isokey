import board
import adafruit_midi
import usb_midi
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import MatrixScanner
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.modules.midi import MidiKeys
from kmk.keys import KC
from kmk.keys import Key
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.control_change import ControlChange
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop

import digitalio
import board

from adafruit_hx711.analog_in import AnalogIn

from adafruit_hx711.hx711 import HX711

data = digitalio.DigitalInOut(board.D13)
data.direction = digitalio.Direction.INPUT

clock = digitalio.DigitalInOut(board.D12)
clock.direction = digitalio.Direction.OUTPUT

hx711 = HX711(data, clock)
channel_a = AnalogIn(hx711, HX711.CHAN_A_GAIN_64)
channel_b = AnalogIn(hx711, HX711.CHAN_B_GAIN_32)

def conv(n):
    n = n & 0xffffff
    return n | (-(n & 0x800000)) + 540000

while True:
    print(f"Reading {conv(channel_a.value)}")
