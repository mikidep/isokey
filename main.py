import board
import adafruit_midi
import usb_midi

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import MatrixScanner, DiodeOrientation
from kmk.modules.layers import Layers
from kmk.modules.midi import MidiKeys
from kmk.keys import KC
from kmk.keys import Key
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.cc import NoteOn
from adafruit_midi.control_change import ControlChange
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop
from kmk.modules import Module

keyboard = KMKKeyboard()

keyboard.row_pins = (
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
)
keyboard.col_pins = (
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
)
keyboard.diode_orientation = DiodeOrientation.COL2ROW
keyboard.matrix = MatrixScanner(
    row_pins=keyboard.row_pins,
    column_pins=keyboard.col_pins,
    columns_to_anodes=keyboard.diode_orientation,
    interval=0.03,
)

keyboard.modules.append(Layers())
keyboard.extensions.append(MidiKeys())

# State
transpose = 60
generator_row = 2
generator_col = 5
lowest_note = 48

midi_output = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

def compute_note(row, col):
    return lowest_note + row * generator_row + col * generator_col

def MidiKey(row, col):
    def key_on_press(key, keyboard, *args, **kwargs):
        midi_output.send(NoteOn(compute_note(row, col), 127, channel=None))
    def key_on_release(key, keyboard, *args, **kwargs):
        midi_output.send(NoteOff(compute_note(row, col), 127, channel=None))
    return Key(on_press=key_on_press, on_release=key_on_release)

def simple_key_builder(f):
  def builder(*builder_args):
    def key_on_press(key, keyboard, *args, **kwargs):
        f(*builder_args)
    def key_on_release(key, keyboard, *args, **kwargs):
        pass
    return Key(on_press=key_on_press, on_release=key_on_release)
  return builder

SetGeneratorRowKey = simple_key_builder(lambda value: generator_row = value)
SetGeneratorColKey = simple_key_builder(lambda value: generator_col = value)
TransposeKey = simple_key_builder(lambda value: transpose += value)
MidiCC = simple_key_builder(lambda value: midi_output.send(ControlChange(value, channel=None)))

keyboard.keymap = [
    [
        MidiKey(0, 1), MidiKey(0, 2),  MidiKey(0, 3),
        MidiKey(1, 1), MidiKey(1, 2),  MidiKey(1, 3),
        MidiKey(2, 1), MidiKey(2, 2),  KC.MO(1),
    ],
    [
        TransposeKey(1), TransposeKey(-1), MidiCC(2),
        SetGeneratorRowKey(1), SetGeneratorRowKey(2), SetGeneratorRowKey(3),
        SetGeneratorColKey(1), SetGeneratorColKey(2), SetGeneratorColKey(3),
    ],
]

if __name__ == "__main__":
    keyboard.go()
