import board
import adafruit_midi
import usb_midi

from typing import Literal, Optional
from dataclasses import dataclass

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


type KeyName = Literal[
    "RTH",
    "R1",
    "R2",
    "R3",
    "R4",
    "L1",
    "L2",
    "L3",
    "L4",
    "RTC",  # Right hand top corner
    "LBC",  # Left hand bottom corner
]

type KeyState = dict[KeyName, bool]


@dataclass
class EWIState:
    key_state: KeyState = dict()
    current_note: Optional[int] = None


state = EWIState()

midi_output = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


def note_map(ks: KeyState) -> Optional[int]:
    pass


def react_and_update_current():
    global state
    new_note = note_map(state.key_state)
    if new_note is not None:
        midi_output.send(NoteOn(new_note, 127, channel=None))
    if state.current_note is not None:
        midi_output.send(NoteOff(state.current_note, 127, channel=None))
    state.current_note = new_note


def EWIKey(kn: KeyName):
    def key_on_press(key, keyboard, *args, **kwargs):
        global state
        state.key_state[kn] = True
        react_and_update_current()

    def key_on_release(key, keyboard, *args, **kwargs):
        global state
        state.key_state[kn] = False
        react_and_update_current()

    return Key(on_press=key_on_press, on_release=key_on_release)


EK = EWIKey

# fmt: off
keyboard.keymap = [
    [
        EK('LBC'), EK('L4'), EK('L3'), EK('L2'), EK('L1'), KC.NO,
        EK('R4'), EK('R3'), EK('R2'), EK('R1'), EK('RTC'), EK('RTH'),
    ],
]
# fmt: on

if __name__ == "__main__":
    keyboard.go()
