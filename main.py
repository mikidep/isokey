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
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
)
keyboard.col_pins = (
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP21,
    board.GP22,
)
keyboard.diode_orientation = DiodeOrientation.COL2ROW
keyboard.matrix = MatrixScanner(
    row_pins=keyboard.row_pins,
    column_pins=keyboard.col_pins,
    columns_to_anodes=keyboard.diode_orientation,
    interval=0.001,
)

keyboard.modules.append(Layers())

# State
generator_row = 7
generator_col = 2
lowest_note = 33

midi_output = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


def compute_note(row, col):
    def lazynote():
        global lowest_note, generator_row, generator_col
        return lowest_note + row * generator_row + col * generator_col

    return lazynote


def LazyMidiNoteKey(lazynote):
    def key_on_press(key, keyboard, *args, **kwargs):
        note = lazynote()
        midi_output.send(NoteOn(note, 127, channel=None))
        print("NOTE:", note)

    def key_on_release(key, keyboard, *args, **kwargs):
        note = lazynote()
        midi_output.send(NoteOff(note, 127, channel=None))
        print("RELEASE ", note)

    return Key(on_press=key_on_press, on_release=key_on_release)


def TransposeKey(offset):
    def key_on_press(key, keyboard, *args, **kwargs):
        global lowest_note
        lowest_note += offset

    return Key(on_press=key_on_press)


def ChangeRowStepKey(offset):
    def key_on_press(key, keyboard, *args, **kwargs):
        global generator_row
        generator_row += offset

    return Key(on_press=key_on_press)


def ChangeColStepKey(offset):
    def key_on_press(key, keyboard, *args, **kwargs):
        global generator_col
        generator_col += offset

    return Key(on_press=key_on_press)


def SetLayoutKey(rowgen, colgen):
    def key_on_press(key, keyboard, *args, **kwargs):
        global generator_row, generator_col
        generator_row = rowgen
        generator_col = colgen

    return Key(on_press=key_on_press)


def GridKey(row, col, octave=0):
    return LazyMidiNoteKey(compute_note(row, col))


GK = GridKey
TK = TransposeKey
CRK = ChangeRowStepKey
CCK = ChangeColStepKey
SLK = SetLayoutKey

# fmt: off
keyboard.keymap = [
    []
    + [KC.NO] + [ GK(0, i) for i in range(10) ] \
    + [ GK(1, i-1) for i in range(11) ] \
    + [KC.NO] + [ GK(2, i-1) for i in range(10) ] \
    + [ GK(3, i-2) for i in range(11) ] \
    + [KC.NO] + [ GK(4, i-2) for i in range(10) ] \
    + [ GK(5, i-3) for i in range(11) ] \
    + [KC.NO] + [ GK(6, i-3) for i in range(10) ] \
    + [ GK(7, i-4) for i in range(11) ] \
    + [KC.MO(1)] + [ GK(8, i-4) for i in range(10) ] \
    ,
    [
        KC.NO, TK(-12), TK(+12), TK(-1), TK(+1),
        CRK(-1), CRK(+1), CCK(-1), CCK(+1),
        SLK(1, 2), # Janko
        SLK(7, 2), # Wicki-Hayden
    ] + [KC.NO for _ in range(100)]
]
# fmt: on

if __name__ == "__main__":
    keyboard.go()
