import board
import adafruit_midi
import usb_midi

# from typing import Literal, Optional
# from dataclasses import dataclass

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
    # interval=0.03,
)

keyboard.modules.append(Layers())

HumanEditableMappings = [
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [1, 1, 1, 1], "C": [0, 0], "N": 60}, # C4
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [1, 1, 1, 0], "C": [0, 0], "N": 62}, # D4
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [1, 1, 0, 0], "C": [0, 0], "N": 64}, # E4
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [1, 0, 0, 0], "C": [0, 0], "N": 65}, # F4
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 67}, # G4
    {"LTH": 0, "L": [1, 1, 0, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 69}, # A4
    {"LTH": 0, "L": [1, 0, 0, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 71}, # B4
    {"LTH": 0, "L": [0, 1, 0, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 72}, # C5

    {"LTH": 0, "L": [1, 1, 1, 1], "R": [1, 1, 1, 1], "C": [0, 0], "N": 61}, # C#5
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [1, 1, 0, 1], "C": [0, 0], "N": 63}, # D#5
    {"LTH": 0, "L": [1, 1, 1, 1], "R": [1, 1, 1, 0], "C": [0, 0], "N": 63}, # D#5
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [0, 1, 0, 0], "C": [0, 0], "N": 66}, # F#5
    {"LTH": 0, "L": [1, 1, 1, 0], "R": [1, 0, 1, 0], "C": [0, 0], "N": 66}, # F#5
    {"LTH": 0, "L": [1, 1, 1, 1], "R": [0, 0, 0, 0], "C": [0, 0], "N": 68}, # G#5
    {"LTH": 0, "L": [1, 1, 0, 1], "R": [0, 0, 0, 0], "C": [0, 0], "N": 68}, # G#5
    {"LTH": 0, "L": [1, 1, 0, 0], "R": [1, 0, 0, 0], "C": [0, 0], "N": 70}, # A#5

    {"LTH": 1, "L": [1, 1, 1, 0], "R": [1, 1, 1, 1], "C": [0, 0], "N": 60 + 12}, # C5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [1, 1, 1, 0], "C": [0, 0], "N": 62 + 12}, # D5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [1, 1, 0, 0], "C": [0, 0], "N": 64 + 12}, # E5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [1, 0, 0, 0], "C": [0, 0], "N": 65 + 12}, # F5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 67 + 12}, # G5
    {"LTH": 1, "L": [1, 1, 0, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 69 + 12}, # A5
    {"LTH": 1, "L": [1, 0, 0, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 71 + 12}, # B5
    {"LTH": 1, "L": [0, 1, 0, 0], "R": [0, 0, 0, 0], "C": [0, 0], "N": 72 + 12}, # C6

    {"LTH": 1, "L": [1, 1, 1, 1], "R": [1, 1, 1, 1], "C": [0, 0], "N": 61 + 12}, # C#5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [1, 1, 0, 1], "C": [0, 0], "N": 63 + 12}, # D#5
    {"LTH": 1, "L": [1, 1, 1, 1], "R": [1, 1, 1, 0], "C": [0, 0], "N": 63 + 12}, # D#5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [0, 1, 0, 0], "C": [0, 0], "N": 66 + 12}, # F#5
    {"LTH": 1, "L": [1, 1, 1, 0], "R": [1, 0, 1, 0], "C": [0, 0], "N": 66 + 12}, # F#5
    {"LTH": 1, "L": [1, 1, 1, 1], "R": [0, 0, 0, 0], "C": [0, 0], "N": 68 + 12}, # G#5
    {"LTH": 1, "L": [1, 1, 0, 0], "R": [1, 0, 0, 0], "C": [0, 0], "N": 70 + 12}, # A#5
]

# type KeyState = dict[KeyName, bool]

class EWIState:
    def __init__(self):
        self.key_state = { 'LTH': False, 'L1': False, 'L2': False, 'L3': False, 'L4': False, 'R1': False, 'R2': False, 'R3': False, 'R4': False, 'RTC': False, 'LBC': False, }
        self.current_note = None

class Mapping:
    def __init__(self, key_state, note: int):
        self.key_state = key_state
        self.note = note

def human_mapping_to_mapping(m) -> Mapping:
    return Mapping(key_state={
        'LTH': m['LTH'],
        'L1': m['L'][0],
        'L2': m['L'][1],
        'L3': m['L'][2],
        'L4': m['L'][3],
        'R1': m['R'][0],
        'R2': m['R'][1],
        'R3': m['R'][2],
        'R4': m['R'][3],
        'RTC': m['C'][1],
        'LBC': m['C'][0],
    }, note=m['N'])

# type KeyName = Literal[
#     "LTH",
#     "R1",
#     "R2",
#     "R3",
#     "R4",
#     "L1",
#     "L2",
#     "L3",
#     "L4",
#     "RTC",  # Right hand top corner
#     "LBC",  # Left hand bottom corner
# ]

Mappings: list[Mapping] = [human_mapping_to_mapping(m) for m in HumanEditableMappings]

State = EWIState()

MidiOutput = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

def is_key_state_equal(ks1: KeyState, ks2: KeyState) -> bool:
    for k in ks1.keys():
        if ks1[k] != ks2.get(k, 0):
            return False
    return True

def note_map(ks: KeyState) -> Optional[int]:
    for mapping in Mappings:
        if is_key_state_equal(ks, mapping.key_state):
            return mapping.note
    return None

def on_actual_key_change():
    global State
    new_note = note_map(State.key_state)
    if new_note is not None:
        MidiOutput.send(NoteOn(new_note, 127, channel=None))
    if State.current_note is not None:
        MidiOutput.send(NoteOff(State.current_note, 127, channel=None))
    State.current_note = new_note

def EWIKey(kn: KeyName):
    def key_on_press(key, keyboard, *args, **kwargs):
        global State
        State.key_state[kn] = True
        on_actual_key_change()

    def key_on_release(key, keyboard, *args, **kwargs):
        global State
        State.key_state[kn] = False
        on_actual_key_change()

    return Key(on_press=key_on_press, on_release=key_on_release)

EK = EWIKey

# fmt: off
keyboard.keymap = [
    [
        EK('LBC'), EK('L4'), EK('L3'), EK('L2'), EK('L1'), KC.NO,
        EK('R4'), EK('R3'), EK('R2'), EK('R1'), EK('RTC'), EK('LTH'),
    ],
]
# fmt: on

if __name__ == "__main__":
    keyboard.go()
