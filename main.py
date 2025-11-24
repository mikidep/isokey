import board
import adafruit_midi
import usb_midi

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

keyboard = KMKKeyboard()

keyboard.row_pins = (
    board.IO9,
    board.IO10,
)
keyboard.col_pins = (
    board.IO1,
    board.IO2,
    board.IO3,
    board.IO4,
    board.IO5,
    board.IO6,
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
generator_row = 1
generator_col = 2
lowest_note = 48

midi_output = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


def compute_note(row, col, octave):
    return lowest_note + 12 * octave + row * generator_row + col * generator_col


def MidiKey(row, col, octave=0):
    def key_on_press(key, keyboard, *args, **kwargs):
        midi_output.send(NoteOn(compute_note(row, col, octave), 127, channel=None))

    def key_on_release(key, keyboard, *args, **kwargs):
        midi_output.send(NoteOff(compute_note(row, col, octave), 127, channel=None))

    return Key(on_press=key_on_press, on_release=key_on_release)


def simple_key_builder(f):
    def builder(*builder_args):
        def key_on_press(key, keyboard, *args, **kwargs):
            f(*builder_args)

        def key_on_release(key, keyboard, *args, **kwargs):
            pass

        return Key(on_press=key_on_press, on_release=key_on_release)

    return builder


# SetGeneratorRowKey = simple_key_builder(lambda value: generator_row = value)
# SetGeneratorColKey = simple_key_builder(lambda value: generator_col = value)
# TransposeKey = simple_key_builder(lambda value: transpose += value)
MidiCC = simple_key_builder(
    lambda value: midi_output.send(ControlChange(value, channel=None))
)

MK = MidiKey

# fmt: off
keyboard.keymap = [
    [
        MK(0, 0), MK(0, 1), MK(0, 2), MK(0, 3), MK(0, 4), KC.NO,
        MK(1, 0), MK(1, 1), MK(1, 2), MK(1, 3), MK(1, 4), KC.MO(1),
        # KC.MO(1),
    ],
        [
        MK(0, 0, 1), MK(0, 1, 1), MK(0, 2, 1), MK(0, 3, 1), MK(0, 4, 1), KC.NO,
        MK(1, 0, 1), MK(1, 1, 1), MK(1, 2, 1), MK(1, 3, 1), MK(1, 4, 1), KC.NO,
        # KC.MO(1),
    ],
    # [
    #     TransposeKey(1), TransposeKey(-1), MidiCC(2),
    #     SetGeneratorRowKey(1), SetGeneratorRowKey(2), SetGeneratorRowKey(3),
    #     SetGeneratorColKey(1), SetGeneratorColKey(2), SetGeneratorColKey(3),
    # ],
]
# fmt: on

if __name__ == "__main__":
    keyboard.go()
