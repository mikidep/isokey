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
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.program_change import ProgramChange
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

keyboard.modules.append(Layers())  # enable layer support

midi = MidiKeys()
keyboard.extensions.append(midi)

TRANSPOSE_DOWN = KC.F12
LAYER_TOGGLE = KC.TG(1)  # toggles layer 1

transpose = 60  # current semitone offset

midi_output = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

def key_on_press(key, keyboard, *args, **kwargs):
    print(key, keyboard)
    midi_output.send(NoteOn(transpose, 127, channel=None))
def key_on_release(key, keyboard, *args, **kwargs):
    print(key, keyboard)
    midi_output.send(NoteOff(transpose, 127, channel=None))

def transpose_on_press(key, keyboard, *args, **kwargs):
    global transpose
    print(key, keyboard)
    transpose += 1
def transpose_on_release(key, keyboard, *args, **kwargs):
    pass

def MidiKey(key):
    return Key(on_press=key_on_press, on_release=key_on_release)

def TransposeKey(delta):
    return Key(on_press=transpose_on_press, on_release=transpose_on_release)

# Build minimal keymap with MIDI notes
KEYMAP = [
    # Layer 0: Playing layer (add toggle key in first position)
    [
        MidiKey(60), MidiKey(60),  MidiKey(60),  MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60), MidiKey(60), MidiKey(60),MidiKey(60),
        MidiKey(60), MidiKey(60),  MidiKey(60),  MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60),MidiKey(60),TransposeKey(1),TransposeKey(1),TransposeKey(1), TransposeKey(1), TransposeKey(1),TransposeKey(1),
        TransposeKey(1), TransposeKey(1),  TransposeKey(1),  TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1), TransposeKey(1), TransposeKey(1),TransposeKey(1),
        TransposeKey(1), TransposeKey(1),  TransposeKey(1),  TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1), TransposeKey(1), TransposeKey(1),TransposeKey(1),
        TransposeKey(1), TransposeKey(1),  TransposeKey(1),  TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1),TransposeKey(1), TransposeKey(1), TransposeKey(1),TransposeKey(1),
    ],
    # Layer 1: Transposition layer (include toggle so user can exit layer)
    [
        MidiKey(60),
        TRANSPOSE_DOWN,
        KC.NO,
        KC.NO,
    ],
]

keyboard.keymap = KEYMAP

# Intercept MIDI notes and apply transpose
old_midi_process = midi.process_key

base_note = 60

def midi_with_transpose(key, pressed):
    global transpose
    print("asdjij", key, pressed)
    # Update transpose if transpose keys pressed
    if pressed:
        if key == MidiKey(60):
            transpose += 1
        elif key == TRANSPOSE_DOWN:
            transpose -= 1
    # Apply transpose to MIDI notes right before processing
    key.note = base_note + transpose
    return old_midi_process(key, pressed)

midi.process_key = midi_with_transpose

if __name__ == "__main__":
    keyboard.go()
