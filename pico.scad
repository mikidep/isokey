include <./prelude.scad>

BW = 21; // Board width (connector side)
BL = 51; // Board length
ISW = 11.4; // Inter-screw width
SO = 2; // Distance between connector edge and center of top screws
ISL = BL - 2 * SO; // Inter-screw length
USBE = 1.3; // USB socket excess length

// Screw hole: M2

CONNTH = 2.5;
CONNW = 8;

// Connector is placed on the Y+ face
function pico_ftp(anchor = TOP, spin = 0) =
  square([BW, BL], anchor = anchor, spin = spin);

function pico_scrws(anchor = TOP, spin = 0) =
  let (p = square([ISW, ISL], anchor = CENTER))
    reorient(anchor, spin, two_d = true, size = [BW, BL], p = p);

A = TOP;
S = -90;

region(pico_ftp(anchor = A, spin = S));
debug_pts(pico_scrws(anchor = A, spin = S));
