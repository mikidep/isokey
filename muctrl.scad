include <./prelude.scad>
use <./jl_scad/box.scad>
use <./jl_scad/parts.scad>
include <./jl_scad/prelude.scad>

USB_RECT = rect([9, 3.7], chamfer = 0.5, anchor = TOP);
MU_SIZE = [18, 23.5];
PCB_TH = 1.6;

module mupart(standoff) {
  box_half(BOT, inside = true)
    box_pos(BOT, RIGHT)
      back(standoff - PCB_TH)
        box_cutout(USB_RECT, chamfer = 1);
  box_half(BOT, inside = true)
    box_pos(BOT + RIGHT, BOT)
      zrot(90) {
        xflip_copy()
          left(MU_SIZE.x / 2) {
            //back(MU_SIZE.y / 2) {
            //  W = 3;
            //  TH = 3;
            //  SLOT = 2;
            //
            //  right(SLOT)
            //    cube([W, TH, standoff - PCB_TH], anchor = BOT + FRONT + RIGHT)
            //      position(TOP + LEFT)
            //        cube([W - SLOT, TH, PCB_TH], anchor = BOT + LEFT);
            //}
            back(MU_SIZE.y) {
              W = 3;
              TH = 3;
              SLOT = 0.75;

              fwd(SLOT)
                cube([W, TH, standoff - PCB_TH], anchor = BOT + FRONT + LEFT) {
                  position(TOP + BACK)
                    cube([W, TH - SLOT, PCB_TH], anchor = BACK + BOT);
                  position(TOP + BACK)
                    up(PCB_TH)
                      cuboid([W, TH - SLOT / 2, PCB_TH], anchor = BACK + BOT, chamfer = SLOT / 2, edges = [FRONT + TOP, FRONT + BOTTOM]);
                }
            }
          }
      }
}

render()
  box_make(halves = [BOT])
    box_shell_base_lid([90, 90, 30], walls_outside = true, rim_height = 0, rtop = 0) {
      mupart(8);
    }

