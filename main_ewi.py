import asyncio
import board
import adafruit_midi
import usb_midi

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import MatrixScanner
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.keys import KC
from kmk.keys import Key
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from kmk.utils import Debug

debug = Debug('kmk.keyboard')

debug.enabled = False

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

class EWIState:
    def __init__(self):
        self.key_state = { 'LTH': False, 'L1': False, 'L2': False, 'L3': False, 'L4': False, 'R1': False, 'R2': False, 'R3': False, 'R4': False, 'C2': False, 'C1': False, }
        self.current_note = None
        self.note_delay_task = None
        self.note_delay = 40
        self.transpose = 0
        self.octave = 0

class Mapping:
    def __init__(self, key_state, action: int | str):
        self.key_state = key_state
        self.action = action

def midi_to_key_name(midi_note: int) -> str:
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return f"{note_names[midi_note % 12]}{midi_note // 12}"

def action_to_string(c):
    return midi_to_key_name(get_note(c)) if type(c) == int else str(c)

# -----------------------------------

def transpose_action(d):
    def transpose_fn(s):
        s.transpose += d
    return transpose_fn

HumanEditableMappingsSax = [

    # Special low octave

    {"LTH": 0, "L": [0,1,0,0], "R": [1,1,1,1], "C": [0,0], "A": 57}, # A2

    {"LTH": 0, "L": [1,1,0,0], "R": [1,1,0,0], "C": [0,0], "A": 57}, # A2 (alt less on right)
    {"LTH": 0, "L": [1,1,0,0], "R": [1,1,1,0], "C": [0,0], "A": 57}, # A2 (alt less on right)
    {"LTH": 0, "L": [1,1,0,0], "R": [1,1,1,1], "C": [0,0], "A": 57}, # A2 (alt less on right)

    {"LTH": 0, "L": [1,0,0,1], "R": [1,1,1,1], "C": [0,0], "A": 58}, # A#2
    {"LTH": 0, "L": [1,0,1,0], "R": [1,1,1,1], "C": [0,0], "A": 58}, # A#2
    {"LTH": 0, "L": [0,0,0,1], "R": [1,1,1,1], "C": [0,0], "A": 58}, # A#2

    {"LTH": 0, "L": [1,0,0,0], "R": [1,1,0,0], "C": [0,0], "A": 59}, # B2 (less on right)
    {"LTH": 0, "L": [1,0,0,0], "R": [1,1,1,0], "C": [0,0], "A": 59}, # B2 (less on right)
    {"LTH": 0, "L": [1,0,0,0], "R": [1,1,1,1], "C": [0,0], "A": 59}, # B2 (less on right)

    # Standard

    {"LTH": 0, "L": [0,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 - 12}, # C2
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60},      # C3
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 + 12}, # C4
    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 + 24}, # C5

    {"LTH": 0, "L": [0,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 - 12}, # D2
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62},      # D3
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 + 12}, # D4
    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 + 24}, # D5
    {"LTH": 0, "L": [0,0,0,0], "R": [0,1,0,0], "C": [0,0], "A": 62 + 12}, # D4 (alt)
    {"LTH": 1, "L": [0,0,0,0], "R": [0,1,0,0], "C": [0,0], "A": 62 + 12}, # D5 (alt)

    {"LTH": 0, "L": [0,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 - 12}, # E2
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64},      # E3
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 + 12}, # E4
    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 + 24}, # E5

    {"LTH": 0, "L": [0,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 - 12}, # F2
    {"LTH": 0, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65},      # F3
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 + 12}, # F4
    {"LTH": 1, "L": [0,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 + 24}, # F5
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,0,1], "C": [0,0], "A": 65 + 24}, # F5 (pinky)

    {"LTH": 0, "L": [0,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 - 12}, # G2
    {"LTH": 0, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67},      # G3
    {"LTH": 1, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 + 12}, # G4
    {"LTH": 1, "L": [0,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 + 24}, # G5
    {"LTH": 1, "L": [1,1,1,0], "R": [0,0,0,1], "C": [0,0], "A": 67 + 24}, # G5 (pinky)

    {"LTH": 0, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69},      # A3
    {"LTH": 1, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69 + 12}, # A4
    {"LTH": 1, "L": [1,1,0,0], "R": [0,0,0,1], "C": [0,0], "A": 69 + 24}, # A5

    {"LTH": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71},      # B3
    {"LTH": 1, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71 + 12}, # B4
    {"LTH": 1, "L": [1,0,0,0], "R": [0,0,0,1], "C": [0,0], "A": 71 + 24}, # B4 (pinky)

    {"LTH": 0, "L": [0,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 72},      # C4
    {"LTH": 1, "L": [0,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 72 + 12}, # C5
    {"LTH": 1, "L": [0,1,0,0], "R": [0,0,0,1], "C": [0,0], "A": 72 + 24}, # C5 (pinky)

    # Accidentals

    {"LTH": 0, "L": [0,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61 - 12}, # C#2
    {"LTH": 0, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61},      # C#3
    {"LTH": 1, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61 + 12}, # C#4
    {"LTH": 1, "L": [0,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61 + 24}, # C#5
    {"LTH": 0, "L": [0,1,0,0], "R": [0,1,0,0], "C": [0,0], "A": 61 + 12}, # C#4 (alt)
    {"LTH": 1, "L": [0,1,0,0], "R": [0,1,0,0], "C": [0,0], "A": 61 + 24}, # C#5 (alt)
    {"LTH": 1, "L": [0,1,0,0], "R": [0,1,0,1], "C": [0,0], "A": 61 + 24}, # C#6 (alt pinky)

    {"LTH": 0, "L": [0,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63 - 12}, # D#2
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63},      # D#3
    {"LTH": 0, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,0], "A": 63},      # D#3
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63 + 12}, # D#4
    {"LTH": 1, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,0], "A": 63 + 12}, # D#4
    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63 + 24}, # D#5
    {"LTH": 1, "L": [0,1,1,1], "R": [1,1,1,0], "C": [0,0], "A": 63 + 24}, # D#5

    {"LTH": 0, "L": [0,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66 - 12}, # F#3
    {"LTH": 0, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66},      # F#3
    {"LTH": 0, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,0], "A": 66},      # F#3
    {"LTH": 1, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66 + 12}, # F#4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,0], "A": 66 + 12}, # F#4
    {"LTH": 1, "L": [0,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66 + 24}, # F#5
    {"LTH": 1, "L": [0,1,1,0], "R": [1,0,1,0], "C": [0,0], "A": 66 + 24}, # F#5
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,1,1], "C": [0,0], "A": 66 + 24}, # F#5 (pinky)

    {"LTH": 0, "L": [0,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68 - 12}, # G#2
    {"LTH": 0, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68},      # G#3
    {"LTH": 0, "L": [1,1,0,1], "R": [0,0,0,0], "C": [0,0], "A": 68},      # G#3
    {"LTH": 1, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68 + 12}, # G#4
    {"LTH": 1, "L": [1,1,0,1], "R": [0,0,0,0], "C": [0,0], "A": 68 + 12}, # G#4
    {"LTH": 1, "L": [0,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68 + 24}, # G#5
    {"LTH": 1, "L": [0,1,1,1], "R": [0,0,0,1], "C": [0,0], "A": 68 + 24}, # G#5 (pinky)

    {"LTH": 0, "L": [0,1,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70 - 12}, # A#2
    {"LTH": 0, "L": [1,1,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70},      # A#3
    {"LTH": 0, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70},      # A#3
    {"LTH": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,1], "A": 70},      # A#3
    {"LTH": 0, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,1], "A": 70},      # A#3
    {"LTH": 1, "L": [1,1,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70 + 12}, # A#4
    {"LTH": 1, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70 + 12}, # A#4
    {"LTH": 1, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,1], "A": 70 + 12}, # A#4
    {"LTH": 1, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,1], "A": 70 + 12}, # A#4
    {"LTH": 1, "L": [1,1,0,0], "R": [1,0,0,1], "C": [0,0], "A": 70 + 12}, # A#4 (pinky)
    {"LTH": 1, "L": [1,0,0,0], "R": [1,0,0,1], "C": [0,0], "A": 70 + 12}, # A#4 (pinky)
    {"LTH": 1, "L": [1,0,0,0], "R": [0,0,0,1], "C": [0,1], "A": 70 + 12}, # A#4 (pinky)
    {"LTH": 1, "L": [1,0,0,0], "R": [1,0,0,1], "C": [0,1], "A": 70 + 12}, # A#4 (pinky)

    # Controls

    {"LTH": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [1,0], "A": "O-"}, # Octave down
    {"LTH": 0, "L": [0,1,0,0], "R": [0,0,0,0], "C": [1,0], "A": "T-"}, # Transpose down
    {"LTH": 0, "L": [0,0,1,0], "R": [0,0,0,0], "C": [1,0], "A": "D-"}, # Delay down 5 milliseconds

    {"LTH": 0, "L": [0,0,0,0], "R": [1,0,0,0], "C": [1,0], "A": "O+"}, # Octave up
    {"LTH": 0, "L": [0,0,0,0], "R": [0,1,0,0], "C": [1,0], "A": "T+"}, # Transpose up
    {"LTH": 0, "L": [0,0,0,0], "R": [0,0,1,0], "C": [1,0], "A": "D+"}, # Delay up 5 milliseconds

    # Copies with bis key

    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,1], "A": 60},      # C3
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,1], "A": 62},      # D3
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,1], "A": 64},      # E3
    {"LTH": 0, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,1], "A": 65},      # F3
    {"LTH": 0, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,1], "A": 67},      # G3
    {"LTH": 0, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,1], "A": 69},      # A3
    {"LTH": 0, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,1], "A": 61},      # C#3
    {"LTH": 0, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,1], "A": 63},      # D#3
    {"LTH": 0, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,1], "A": 63},      # D#3
    {"LTH": 0, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,1], "A": 66},      # F#3
    {"LTH": 0, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,1], "A": 66},      # F#3
    {"LTH": 0, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,1], "A": 68},      # G#3
    {"LTH": 0, "L": [1,1,0,1], "R": [0,0,0,0], "C": [0,1], "A": 68},      # G#3

    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,1], "A": 60 + 12}, # C4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,1], "A": 62 + 12}, # D4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,1], "A": 64 + 12}, # E4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,1], "A": 65 + 12}, # F4
    {"LTH": 1, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,1], "A": 67 + 12}, # G4
    {"LTH": 1, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,1], "A": 69 + 12}, # A4
    {"LTH": 1, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,1], "A": 61 + 12}, # C#4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,1], "A": 63 + 12}, # D#4
    {"LTH": 1, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,1], "A": 63 + 12}, # D#4
    {"LTH": 1, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,1], "A": 66 + 12}, # F#4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,1], "A": 66 + 12}, # F#4
    {"LTH": 1, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,1], "A": 68 + 12}, # G#4
]

HumanEditableMappingsFlute = [
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60}, # C4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62}, # D4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64}, # E4
    {"LTH": 1, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65}, # F4
    {"LTH": 1, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67}, # G4
    {"LTH": 1, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69}, # A4
    {"LTH": 1, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71}, # B4
    {"LTH": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 72}, # C5

    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 + 12}, # C5
    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 + 12}, # D5
    {"LTH": 1, "L": [0,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 + 12}, # E5
    {"LTH": 1, "L": [0,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 + 12}, # F5
    {"LTH": 1, "L": [0,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 + 12}, # G5
    {"LTH": 1, "L": [0,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69 + 12}, # A5
    {"LTH": 1, "L": [0,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71 + 12}, # B5
]

HumanEditableMappings = HumanEditableMappingsSax

def show_human_mapping(m):
    def v(val):
        return '1' if val else '0'
    return f"LTH: {v(m['LTH'])} L:[{v(m['L'][0])} {v(m['L'][1])} {v(m['L'][2])} {v(m['L'][3])}] R:[{v(m['R'][0])} {v(m['R'][1])} {v(m['R'][2])} {v(m['R'][3])}], C:[{v(m['C'][0])}, {v(m['C'][1])}] A: {m['A']}"

def check_for_duplicates():
    seen = {}
    for m in HumanEditableMappings:
        ks = f"{m['LTH']}, {tuple(m['L'])}, {tuple(m['R'])}, {tuple(m['C'])}"
        if ks in seen:
            print("WARNING: Duplicate mapping found:", show_human_mapping(m), "already declared", seen[ks])
        else:
            seen[ks] = m['A']

check_for_duplicates()

def human_mapping_to_mapping(m) -> Mapping:
    return Mapping(key_state={ 'LTH': m['LTH'], 'L1': m['L'][0], 'L2': m['L'][1], 'L3': m['L'][2], 'L4': m['L'][3], 'R1': m['R'][0], 'R2': m['R'][1], 'R3': m['R'][2], 'R4': m['R'][3], 'C1': m['C'][0], 'C2': m['C'][1], }, action=m['A'])

Mappings: list[Mapping] = [human_mapping_to_mapping(m) for m in HumanEditableMappings]

# -----------------------------------

def show_key_state(keys):
    def p(k):
        return '1' if keys[k] else '0'
    return f"LTH: {p('LTH')} L:[{p('L1')} {p('L2')} {p('L3')} {p('L4')}] R:[{p('R1')} {p('R2')} {p('R3')} {p('R4')}], C:[{p('C1')}, {p('C2')}]"

def print_state_keys(state, action: int | str):
    print(f"{show_key_state(state.key_state)} => {action_to_string(action)}")

def print_state_settings(state, action: int | str):
    print(f"Transposition: {state.transpose}, delay: {state.note_delay} ms, action entered: {action_to_string(action)}")

def is_key_state_equal(ks1, ks2) -> bool:
    for k in ks1.keys():
        if ks1[k] != ks2[k]:
            return False
    return True

def is_key_state_empty(ks) -> bool:
    for k in ks.keys():
        if ks[k]:
            return False
    return True

State = EWIState()

MidiOutput = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# -----------------------------------

def get_action(ks) -> int | None:
    for mapping in Mappings:
        if is_key_state_equal(ks, mapping.key_state):
            return mapping.action
    return None

def get_note(action: int):
    return action + State.transpose + State.octave * 12

# Stop everything
def midi_stop_everything():
    if State.current_note is not None:
        MidiOutput.send(NoteOff(State.current_note, 127, channel=None))
    State.current_note = None

# Play the note. Stop the previous one if needed
def midi_play_note(new_note: int):
    if new_note != State.current_note if State.current_note is not None else True:
        MidiOutput.send(NoteOn(new_note, 127, channel=None))
    if State.current_note is not None and State.current_note != new_note:
        MidiOutput.send(NoteOff(State.current_note, 127, channel=None))
    State.current_note = new_note

def actual_key_change():
    action = get_action(State.key_state)
    print_state_keys(State, action)
    if action is None:
        midi_stop_everything()
    elif type(action) == int:
        midi_play_note(get_note(action))

def on_key_change():
    action = get_action(State.key_state)
    if is_key_state_empty(State.key_state):
        midi_stop_everything()
        State.current_note = None
    elif type(action) == str:
        if action == "T-":
            State.transpose -= 1
        elif action == "T+":
            State.transpose += 1
        elif action == "D-":
            State.note_delay -= 5
        elif action == "D+":
            State.note_delay += 5
        elif action == "O-":
            State.octave -= 1
        elif action == "O+":
            State.octave += 1
        print_state_settings(State, action)
    else:
        if State.note_delay_task is not None:
            keyboard.cancel_timeout(State.note_delay_task)
        State.note_delay_task = \
            keyboard.set_timeout(callback=actual_key_change, after_ticks=State.note_delay)

# -----------------------------------

def EWIKey(kn: KeyName):
    def key_on_press(key, keyboard, *args, **kwargs):
        State.key_state[kn] = True
        on_key_change()

    def key_on_release(key, keyboard, *args, **kwargs):
        State.key_state[kn] = False
        on_key_change()

    return Key(on_press=key_on_press, on_release=key_on_release)

EK = EWIKey

# fmt: off
keyboard.keymap = [
    [
        EK('C1'), EK('L4'), EK('L3'), EK('L2'), EK('L1'), KC.NO,
        EK('R4'), EK('R3'), EK('R2'), EK('R1'), EK('C2'), EK('LTH'),
    ],
]
# fmt: on

if __name__ == "__main__":
    keyboard.go()
