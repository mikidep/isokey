import board
import adafruit_midi
import usb_midi
import digitalio

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import MatrixScanner
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.keys import KC
from kmk.keys import Key
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.control_change import ControlChange
from adafruit_midi.channel_pressure import ChannelPressure
from kmk.utils import Debug

from adafruit_hx711.analog_in import AnalogIn
from adafruit_hx711.hx711 import HX711

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
    interval=0.005,
)

keyboard.modules.append(Layers())

class Mapping:
    def __init__(self, key_state, action: int | str):
        self.key_state = key_state
        self.action = action

def midi_to_key_name(midi_note: int) -> str:
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return f"{note_names[midi_note % 12]}{midi_note // 12}"

# -----------------------------------

TICKING_INTERVAL = 1
KEY_STATE = { 'OCT': False, 'L1': False, 'L2': False, 'L3': False, 'L4': False, 'R1': False, 'R2': False, 'R3': False, 'R4': False, 'C2': False, 'C1': False, }
CURRENT_NOTE = None
NOTE_DELAY_TASK = None
NOTE_DELAY = 1
TRANSPOSE = 0
OCTAVE = 0
# Syncronization variable
ACTION_NOTE = None
OUTPUT = None
BREATH = 0.0

# -----------------------------------

data = digitalio.DigitalInOut(board.D13)
data.direction = digitalio.Direction.INPUT

clock = digitalio.DigitalInOut(board.D12)
clock.direction = digitalio.Direction.OUTPUT

hx711 = HX711(data, clock)
channel_a = AnalogIn(hx711, HX711.CHAN_A_GAIN_64)
channel_b = AnalogIn(hx711, HX711.CHAN_B_GAIN_32)

SENSOR_BASELINE = 548608 # 11111111111101111010000100000000

CAPPED_VALUE = 700_000
MIN_VALUE = 80_000

CC_MIDI_CHANNEL = 7

def convert_number(u):
    u &= 0xFFFFFF
    return (u - 0x1000000 if u & 0x800000 else u) + SENSOR_BASELINE

def Breath():
    reading = channel_a.value
    n = abs(convert_number(reading))
    pct = (n - MIN_VALUE) / (CAPPED_VALUE - MIN_VALUE)
    return max(0.0, min(1.0, pct))

# -----------------------------------

# Stop everything
def midi_stop_everything():
    global CURRENT_NOTE, MidiOutput
    if CURRENT_NOTE is not None:
        MidiOutput.send(NoteOff(CURRENT_NOTE, 127, channel=None))
    CURRENT_NOTE = None

# Play the note. Stop the previous one if needed
def midi_play_note(new_note: int):
    global CURRENT_NOTE, MidiOutput
    if new_note != CURRENT_NOTE:
        if new_note is not None:
            MidiOutput.send(NoteOn(new_note, 127, channel=None))
        if CURRENT_NOTE is not None:
            MidiOutput.send(NoteOff(CURRENT_NOTE, 127, channel=None))
    CURRENT_NOTE = new_note

def v01_to_midi(val01: int) -> int:
    # Map breath value 0.0 .. 1.0 to CC value (0-127).
    return int(127 * val01)

def midi_send_breath(val01: int):
    MidiOutput.send(ControlChange(CC_MIDI_CHANNEL, v01_to_midi(val01), channel=None))

def PollFunction():
    global ACTION_NOTE, MidiOutput
    breath = Breath()
    if breath == 0.0:
        midi_stop_everything()
    else:
        print(f"Breath: {breath}")
        midi_play_note(ACTION_NOTE)
        midi_send_breath(breath)
    keyboard.set_timeout(callback=PollFunction, after_ticks=TICKING_INTERVAL)

# -----------------------------------

HumanEditableMappingsSax = [

    # Standard

    {"OCT": 0, "L": [0,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 - 12}, # C2 (holed)
    {"OCT": 0, "L": [0,0,0,0], "R": [1,1,1,1], "C": [0,0], "A": 60 - 12}, # C2
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60},      # C3
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 + 12}, # C4
    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 + 24}, # C5

    {"OCT": 0, "L": [0,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 - 12}, # D2 (holed)
    {"OCT": 0, "L": [0,0,0,0], "R": [1,1,1,0], "C": [0,0], "A": 62 - 12}, # D2
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62},      # D3
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 + 12}, # D4
    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 + 24}, # D5
    {"OCT": 0, "L": [0,0,0,0], "R": [0,1,0,0], "C": [0,0], "A": 62 + 12}, # D4 (side)
    {"OCT": 1, "L": [0,0,0,0], "R": [0,1,0,0], "C": [0,0], "A": 62 + 24}, # D5 (side)

    {"OCT": 0, "L": [0,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 - 12}, # E2 (holed)
    {"OCT": 0, "L": [0,0,0,0], "R": [1,1,0,0], "C": [0,0], "A": 64 - 12}, # E2
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64},      # E3
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 + 12}, # E4
    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 + 24}, # E5

    {"OCT": 0, "L": [0,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 - 12}, # F2 (holed)
    {"OCT": 0, "L": [0,0,0,0], "R": [1,0,0,0], "C": [0,0], "A": 65 - 12}, # F2
    {"OCT": 0, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65},      # F3
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 + 12}, # F4
    {"OCT": 1, "L": [0,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 + 24}, # F5
    {"OCT": 1, "L": [0,1,1,0], "R": [1,0,0,1], "C": [0,0], "A": 65 + 24}, # F5 (pinky intermediate)
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,0,1], "C": [0,0], "A": 65 + 24}, # F5 (pinky)

    {"OCT": 0, "L": [0,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 - 12}, # G2 (holed)
    {"OCT": 0, "L": [0,0,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 - 12}, # G2
    {"OCT": 0, "L": [0,0,1,0], "R": [1,0,0,0], "C": [0,0], "A": 67 - 12}, # G2 (alt more keys)
    {"OCT": 0, "L": [0,0,1,0], "R": [1,1,0,0], "C": [0,0], "A": 67 - 12}, # G2 (alt more keys)
    {"OCT": 0, "L": [0,0,1,0], "R": [1,1,1,0], "C": [0,0], "A": 67 - 12}, # G2 (alt more keys)
    {"OCT": 0, "L": [0,0,1,0], "R": [1,1,1,1], "C": [0,0], "A": 67 - 12}, # G2 (alt more keys)
    {"OCT": 0, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67},      # G3
    {"OCT": 1, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 + 12}, # G4
    {"OCT": 1, "L": [0,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 + 24}, # G5
    {"OCT": 1, "L": [0,1,1,0], "R": [0,0,0,1], "C": [0,0], "A": 67 + 24}, # G5 (pinky intermediate)
    {"OCT": 1, "L": [1,1,1,0], "R": [0,0,0,1], "C": [0,0], "A": 67 + 24}, # G5 (pinky)

    {"OCT": 0, "L": [0,1,0,0], "R": [1,1,1,1], "C": [0,0], "A": 69 - 12}, # A2
    {"OCT": 0, "L": [0,1,0,0], "R": [1,1,1,0], "C": [0,0], "A": 69 - 12}, # A2 (alt more keys)
    {"OCT": 0, "L": [0,1,0,0], "R": [1,1,0,0], "C": [0,0], "A": 69 - 12}, # A2 (alt more keys)
    {"OCT": 0, "L": [1,1,0,0], "R": [1,1,0,0], "C": [0,0], "A": 69 - 12}, # A2 (alt more keys)
    {"OCT": 0, "L": [1,1,0,0], "R": [1,1,1,0], "C": [0,0], "A": 69 - 12}, # A2 (alt more keys)
    {"OCT": 0, "L": [1,1,0,0], "R": [1,1,1,1], "C": [0,0], "A": 69 - 12}, # A2 (alt more keys)
    {"OCT": 0, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69},      # A3
    {"OCT": 1, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69 + 12}, # A4
    {"OCT": 1, "L": [1,1,0,0], "R": [0,0,0,1], "C": [0,0], "A": 69 + 24}, # A5

    {"OCT": 0, "L": [1,0,0,0], "R": [1,1,0,0], "C": [0,0], "A": 59},      # B2 (more keys)
    {"OCT": 0, "L": [1,0,0,0], "R": [1,1,1,0], "C": [0,0], "A": 59},      # B2 (more keys)
    {"OCT": 0, "L": [1,0,0,0], "R": [1,1,1,1], "C": [0,0], "A": 59},      # B2 (more keys)
    {"OCT": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71},      # B3
    {"OCT": 1, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71 + 12}, # B4
    {"OCT": 1, "L": [1,0,0,0], "R": [0,0,0,1], "C": [0,0], "A": 71 + 24}, # B4 (pinky)

    {"OCT": 0, "L": [0,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 72},      # C4
    {"OCT": 1, "L": [0,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 72 + 12}, # C5
    {"OCT": 1, "L": [0,1,0,0], "R": [0,0,0,1], "C": [0,0], "A": 72 + 24}, # C5 (pinky)

    # Accidentals

    {"OCT": 0, "L": [0,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61 - 12}, # C#2
    {"OCT": 0, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61},      # C#3
    {"OCT": 0, "L": [0,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 61 + 12}, # C#4
    {"OCT": 1, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61 + 12}, # C#4
    {"OCT": 1, "L": [0,1,1,1], "R": [1,1,1,1], "C": [0,0], "A": 61 + 24}, # C#5
    {"OCT": 1, "L": [0,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 61 + 24}, # C#5
    {"OCT": 0, "L": [0,1,0,0], "R": [0,1,0,0], "C": [0,0], "A": 61 + 12}, # C#4 (alt)
    {"OCT": 1, "L": [0,1,0,0], "R": [0,1,0,0], "C": [0,0], "A": 61 + 24}, # C#5 (alt)
    {"OCT": 1, "L": [0,1,0,0], "R": [0,1,0,1], "C": [0,0], "A": 61 + 24}, # C#5 (alt pinky)

    {"OCT": 0, "L": [0,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63 - 12}, # D#2
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63},      # D#3
    {"OCT": 0, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,0], "A": 63},      # D#3
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63 + 12}, # D#4
    {"OCT": 1, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,0], "A": 63 + 12}, # D#4
    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,0,1], "C": [0,0], "A": 63 + 24}, # D#5
    {"OCT": 1, "L": [0,1,1,1], "R": [1,1,1,0], "C": [0,0], "A": 63 + 24}, # D#5

    {"OCT": 0, "L": [0,0,0,0], "R": [1,0,1,0], "C": [0,0], "A": 66 - 12}, # F#2
    {"OCT": 0, "L": [0,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66 - 12}, # F#2
    {"OCT": 0, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66},      # F#3
    {"OCT": 0, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,0], "A": 66},      # F#3
    {"OCT": 1, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66 + 12}, # F#4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,0], "A": 66 + 12}, # F#4
    {"OCT": 1, "L": [0,1,1,0], "R": [0,1,0,0], "C": [0,0], "A": 66 + 24}, # F#5
    {"OCT": 1, "L": [0,1,1,0], "R": [1,0,1,0], "C": [0,0], "A": 66 + 24}, # F#5
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,1,1], "C": [0,0], "A": 66 + 24}, # F#5 (pinky)

    {"OCT": 0, "L": [0,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68 - 12}, # G#2
    {"OCT": 0, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68},      # G#3
    {"OCT": 0, "L": [1,1,0,1], "R": [0,0,0,0], "C": [0,0], "A": 68},      # G#3
    {"OCT": 1, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68 + 12}, # G#4
    {"OCT": 1, "L": [1,1,0,1], "R": [0,0,0,0], "C": [0,0], "A": 68 + 12}, # G#4
    {"OCT": 1, "L": [0,1,1,1], "R": [0,0,0,0], "C": [0,0], "A": 68 + 24}, # G#5
    {"OCT": 1, "L": [0,1,1,1], "R": [0,0,0,1], "C": [0,0], "A": 68 + 24}, # G#5 (pinky)

    {"OCT": 0, "L": [1,0,0,1], "R": [1,1,1,1], "C": [0,0], "A": 70 - 12}, # A#2
    {"OCT": 0, "L": [0,0,0,1], "R": [1,1,1,1], "C": [0,0], "A": 70 - 12}, # A#2
    {"OCT": 0, "L": [0,1,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70 - 12}, # A#2
    {"OCT": 0, "L": [1,1,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70},      # A#3
    {"OCT": 0, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70},      # A#3
    {"OCT": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,1], "A": 70},      # A#3
    {"OCT": 0, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,1], "A": 70},      # A#3
    {"OCT": 1, "L": [1,1,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70 + 12}, # A#4
    {"OCT": 1, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,0], "A": 70 + 12}, # A#4
    {"OCT": 1, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,1], "A": 70 + 12}, # A#4
    {"OCT": 1, "L": [1,0,0,0], "R": [1,0,0,0], "C": [0,1], "A": 70 + 12}, # A#4
    {"OCT": 1, "L": [1,1,0,0], "R": [1,0,0,1], "C": [0,0], "A": 70 + 24}, # A#5 (pinky)
    {"OCT": 1, "L": [1,0,0,0], "R": [1,0,0,1], "C": [0,0], "A": 70 + 24}, # A#5 (pinky)
    {"OCT": 1, "L": [1,0,0,0], "R": [0,0,0,1], "C": [0,1], "A": 70 + 24}, # A#5 (pinky)
    {"OCT": 1, "L": [1,0,0,0], "R": [1,0,0,1], "C": [0,1], "A": 70 + 24}, # A#5 (pinky)

    # Controls

    {"OCT": 0, "L": [1,0,0,1], "R": [0,0,0,1], "C": [0,1], "A": "O-"}, # Octave down
    {"OCT": 0, "L": [0,1,0,1], "R": [0,0,0,1], "C": [0,1], "A": "T-"}, # Transpose down
    {"OCT": 0, "L": [0,0,1,1], "R": [0,0,0,1], "C": [0,1], "A": "D-"}, # Delay down 5 milliseconds

    {"OCT": 0, "L": [0,0,0,1], "R": [1,0,0,1], "C": [0,1], "A": "O+"}, # Octave up
    {"OCT": 0, "L": [0,0,0,1], "R": [0,1,0,1], "C": [0,1], "A": "T+"}, # Transpose up
    {"OCT": 0, "L": [0,0,0,1], "R": [0,0,1,1], "C": [0,1], "A": "D+"}, # Delay up 5 milliseconds

    # Copies with bis key

    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,1], "A": 60},      # C3
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,1], "A": 62},      # D3
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,1], "A": 64},      # E3
    {"OCT": 0, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,1], "A": 65},      # F3
    {"OCT": 0, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,1], "A": 67},      # G3
    {"OCT": 0, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,1], "A": 69},      # A3
    {"OCT": 0, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,1], "A": 61},      # C#3
    {"OCT": 0, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,1], "A": 63},      # D#3
    {"OCT": 0, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,1], "A": 63},      # D#3
    {"OCT": 0, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,1], "A": 66},      # F#3
    {"OCT": 0, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,1], "A": 66},      # F#3
    {"OCT": 0, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,1], "A": 68},      # G#3
    {"OCT": 0, "L": [1,1,0,1], "R": [0,0,0,0], "C": [0,1], "A": 68},      # G#3

    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,1], "A": 60 + 12}, # C4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,1], "A": 62 + 12}, # D4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,1], "A": 64 + 12}, # E4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,1], "A": 65 + 12}, # F4
    {"OCT": 1, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,1], "A": 67 + 12}, # G4
    {"OCT": 1, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,1], "A": 69 + 12}, # A4
    {"OCT": 1, "L": [1,1,1,1], "R": [1,1,1,1], "C": [0,1], "A": 61 + 12}, # C#4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,0,1], "C": [0,1], "A": 63 + 12}, # D#4
    {"OCT": 1, "L": [1,1,1,1], "R": [1,1,1,0], "C": [0,1], "A": 63 + 12}, # D#4
    {"OCT": 1, "L": [1,1,1,0], "R": [0,1,0,0], "C": [0,1], "A": 66 + 12}, # F#4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,1,0], "C": [0,1], "A": 66 + 12}, # F#4
    {"OCT": 1, "L": [1,1,1,1], "R": [0,0,0,0], "C": [0,1], "A": 68 + 12}, # G#4
]

HumanEditableMappingsFlute = [
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60}, # C4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62}, # D4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64}, # E4
    {"OCT": 1, "L": [1,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65}, # F4
    {"OCT": 1, "L": [1,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67}, # G4
    {"OCT": 1, "L": [1,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69}, # A4
    {"OCT": 1, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71}, # B4
    {"OCT": 0, "L": [1,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 72}, # C5

    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,1,1], "C": [0,0], "A": 60 + 12}, # C5
    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,1,0], "C": [0,0], "A": 62 + 12}, # D5
    {"OCT": 1, "L": [0,1,1,0], "R": [1,1,0,0], "C": [0,0], "A": 64 + 12}, # E5
    {"OCT": 1, "L": [0,1,1,0], "R": [1,0,0,0], "C": [0,0], "A": 65 + 12}, # F5
    {"OCT": 1, "L": [0,1,1,0], "R": [0,0,0,0], "C": [0,0], "A": 67 + 12}, # G5
    {"OCT": 1, "L": [0,1,0,0], "R": [0,0,0,0], "C": [0,0], "A": 69 + 12}, # A5
    {"OCT": 1, "L": [0,0,0,0], "R": [0,0,0,0], "C": [0,0], "A": 71 + 12}, # B5
]

HumanEditableMappings = HumanEditableMappingsSax

def show_human_mapping(m):
    def v(val):
        return '1' if val else '0'
    return f"OCT: {v(m['OCT'])} L:[{v(m['L'][0])} {v(m['L'][1])} {v(m['L'][2])} {v(m['L'][3])}] R:[{v(m['R'][0])} {v(m['R'][1])} {v(m['R'][2])} {v(m['R'][3])}], C:[{v(m['C'][0])}, {v(m['C'][1])}] A: {m['A']}"

def check_for_duplicates():
    seen = {}
    for m in HumanEditableMappings:
        ks = f"{m['OCT']}, {tuple(m['L'])}, {tuple(m['R'])}, {tuple(m['C'])}"
        if ks in seen:
            print("WARNING: Duplicate mapping found:", show_human_mapping(m), "already declared", seen[ks])
        else:
            seen[ks] = m['A']

check_for_duplicates()

def human_mapping_to_mapping(m) -> Mapping:
    return Mapping(key_state={ 'OCT': m['OCT'], 'L1': m['L'][0], 'L2': m['L'][1], 'L3': m['L'][2], 'L4': m['L'][3], 'R1': m['R'][0], 'R2': m['R'][1], 'R3': m['R'][2], 'R4': m['R'][3], 'C1': m['C'][0], 'C2': m['C'][1], }, action=m['A'])

Mappings: list[Mapping] = [human_mapping_to_mapping(m) for m in HumanEditableMappings]

# -----------------------------------

def show_key_state(keys):
    def p(k):
        return '1' if keys[k] else '0'
    return f"OCT: {p('OCT')} L:[{p('L1')} {p('L2')} {p('L3')} {p('L4')}] R:[{p('R1')} {p('R2')} {p('R3')} {p('R4')}], C:[{p('C1')} {p('C2')}]"

def get_note(action: int):
    return action + TRANSPOSE + OCTAVE * 12

def action_to_string(c):
    return midi_to_key_name(c) if type(c) == int else str(c)

def print_state_keys(action: int | str):
    print(f"{show_key_state(KEY_STATE)} => {action_to_string(action)}" \
          + (f' ({get_note(action)}' \
             + (f' octave: {OCTAVE}, transposition: {TRANSPOSE}' if TRANSPOSE != 0 or OCTAVE != 0 else '') \
             + ')' if type(action) == int else ''))

def print_state_settings(action: int | str):
    print(f"Oct: {OCTAVE}, trans: {TRANSPOSE}, delay: {NOTE_DELAY} ms, action: {action_to_string(action)}")

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

MidiOutput = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# -----------------------------------

def get_action(ks) -> int | None:
    for mapping in Mappings:
        if is_key_state_equal(ks, mapping.key_state):
            return mapping.action
    return None

def actual_key_change():
    global ACTION_NOTE
    action = get_action(KEY_STATE)
    print_state_keys(action)
    if action is None:
        ACTION_NOTE = None
    elif type(action) == int:
        ACTION_NOTE = get_note(action)

def on_key_change():
    global KEY_STATE, NOTE_DELAY_TASK, TRANSPOSE, OCTAVE, NOTE_DELAY
    action = get_action(KEY_STATE)
    if type(action) == str:
        if action == "T-":
            TRANSPOSE -= 1
        elif action == "T+":
            TRANSPOSE += 1
        elif action == "D-":
            NOTE_DELAY = max(0, NOTE_DELAY - 5)
        elif action == "D+":
            NOTE_DELAY = max(0, NOTE_DELAY + 5)
        elif action == "O-":
            OCTAVE -= 1
        elif action == "O+":
            OCTAVE += 1
        print_state_settings(action)
    else:
        if NOTE_DELAY_TASK is not None:
            keyboard.cancel_timeout(NOTE_DELAY_TASK)
        NOTE_DELAY_TASK = \
            keyboard.set_timeout(callback=actual_key_change, after_ticks=NOTE_DELAY)

# -----------------------------------

def EWIKey(kn):
    def key_on_press(key, keyboard, *args, **kwargs):
        KEY_STATE[kn] = True
        on_key_change()

    def key_on_release(key, keyboard, *args, **kwargs):
        KEY_STATE[kn] = False
        on_key_change()

    return Key(on_press=key_on_press, on_release=key_on_release)

EK = EWIKey

# fmt: off
keyboard.keymap = [
    [
        EK('C1'), EK('L4'), EK('L3'), EK('L2'), EK('L1'), KC.NO,
        EK('R4'), EK('R3'), EK('R2'), EK('R1'), EK('C2'), EK('OCT'),
    ],
]
# fmt: on

if __name__ == "__main__":
    print("EWI ready.")
    # Schedule the non-threaded central poll loop via KMK timeouts
    keyboard.set_timeout(callback=PollFunction, after_ticks=TICKING_INTERVAL)
    # Start the keyboard main loop (blocks)
    keyboard.go()
