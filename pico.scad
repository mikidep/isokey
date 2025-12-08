include <./prelude.scad>
use <./jl_scad/box.scad>
use <./jl_scad/parts.scad>
use <./contactModule100.scad>
include <./jl_scad/prelude.scad>

BW = 21; // Board width (connector side)
BL = 51; // Board length
ISW = 11.4; // Inter-screw width
PRW = 17.78; // Pin rectangle width
PRL = 48.26; // Pin rectangle length
MARGIN = 4;
PITCH = 0.1 * INCH;
NPINS_SIDE = 20;

function pico_extra_h() =
  BW + 2 * MARGIN;

function pico_l() = BL;
module pico_ftp() box_half(TOP, inside = false)
  box_pos(BACK + RIGHT) {
    fwd(MARGIN)
      left($box_wall + 0.2)
        #cube([51, 21, 3], anchor = BACK + RIGHT + BOT);
  }

module pico_socket() box_half(TOP, inside = false)
  box_pos(BACK + RIGHT)
    fwd(MARGIN)
      left($box_wall + 1.2)
        left_half(x = 0.5)
          fwd(BW / 2)
            yflip_copy()
              left((BL - PRL) / 2)
                back(BW / 2 - (BW - PRW) / 2)
                  for(i = [0:NPINS_SIDE - 1])
                    left(i * PITCH) {
                      contact_part(blade = false);
                    }

module pico_hole() box_half(TOP, inside = false)
  box_pos(BACK + RIGHT + TOP)
    down(1)
      fwd(MARGIN + BW / 2)
        box_cut() {
          cube([6, 8.5, 4.5], anchor = TOP + RIGHT);
          left($box_wall + 0.4)
            cube([BL, BW, 4.5], anchor = TOP + RIGHT);

        }




module mybox() {
  box_size = [ //
  PITCH * NPINS_SIDE + 20, //
  25, 15 //
  ];
  box_shell_base_lid(box_size, rtop = 0, rbot = 0, rsides = 2, rim_height = 0, k = 0.5, wall_top = PLATE_TH)
    children();
}

module main() box_make(halves = [TOP, BOT], print = true)
  mybox() {
    pico_socket();
    pico_hole();
  }


render()
  main();
