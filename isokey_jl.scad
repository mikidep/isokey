include <prelude.scad>
use <./keys_layout.scad>
use <./jl_scad/box.scad>
use <./jl_scad/parts.scad>
use <./keyModule.scad>
use <./muctrl.scad>
use <./pico.scad>

include <./jl_scad/prelude.scad>

COLS = 10;
ROWS = 9;

//COLS = 4;
//ROWS = 2;

PLATE_DIST = 3;
PLATE_HOLE_SIDE = 14;

keys_pts = keys_pts(COLS, ROWS);
tile_size = tile_size();

tiles_size = tiles_size(COLS, ROWS);

box_size = [ //
tiles_size.x, //
tiles_size.y + pico_extra_h(), //
10 //
];

screw_pts = screw_pts(COLS, ROWS);

module mybox() {
  box_shell_base_lid(box_size, rtop = 0, rbot = 0, rsides = 2, rim_height = 3, wall_top = PLATE_TH, wall_bot = PLATE_TH)
    children();
}

module plate_box() {
  pbox_size = [box_size.x, box_size.y, PLATE_DIST];
  box_shell_base_lid(pbox_size, base_height = PLATE_TH, rtop = 2, rsides = 2, rim_height = 0, wall_top = PLATE_TH, wall_bot = PLATE_TH)
    children();
}

module plate_switch_hole() box_cutout(square([14, 14], anchor = CENTER));

module main() {
  module screw_hole() {
    depth = 2;
    box_screw_clamp(id = 3.4, h = 2, head_d = 3.4, head_depth = depth, chamfer = depth);
  }
  module screw_hole_plate() {
    box_screw_clamp(h = 2, id = 4.6, od = 6.4, head_depth = 0, fillet = 0);
  }
  box_make(halves = [BOT], print = true) {
    mybox() {
      move(tile_size / 2) {
        move(2 * [1, 1])
          box_half(TOP, inside = false) {
            box_pos(FRONT + LEFT) {
              for(p = keys_pts)
                move(p) {
                  key_part();
                }

              for(p = screw_pts)
                move(p) {
                  box_hole(3.2);
                }
            }
          }
        position(FRONT + LEFT)
          for(p = screw_pts)
            move(p) {
              screw_hole();
            }
      }

      //position(BACK + LEFT)
      //  move(yflip([21, 21] / 2 + [15, 0]))
      //    screw_hole();
      box_half(TOP, inside = false) {
        box_pos(BACK + LEFT)
          move(yflip([2, 2] + [21, 21] / 2)) {
            key_part();
          }
      }

      pico_socket();
    }
  }
  //left(box_size.x + 10)
  //  box_make(halves = [TOP], print = true)
  //    plate_box() {
  //      move(tile_size / 2) {
  //        move([2, 2])
  //          box_half(TOP, inside = false) {
  //            box_pos(FRONT + LEFT) {
  //              for(p = keys_pts)
  //                move(p) {
  //                  plate_switch_hole();
  //                }
  //              for(p = screw_pts)
  //                move(p) {
  //                  box_hole(4.2);
  //                }
  //            }
  //          }
  //        position(FRONT + LEFT)
  //          for(p = screw_pts)
  //            move(p) {
  //              screw_hole_plate();
  //            }
  //
  //      //position(BACK + LEFT)
  //      //  move(yflip([21, 21] / 2 + [15, 0]))
  //      //    screw_hole_plate();
  //
  //      }
  //      box_half(TOP, inside = false)
  //        box_pos(BACK + LEFT)
  //          move(yflip([2, 2] + [21, 21] / 2))
  //            plate_switch_hole();
  //      pico_hole();
  //    }
  ;
}

projection(cut = false)
  render()
    main();


