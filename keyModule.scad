include <prelude.scad>
use <contactModule100.scad>
include <./jl_scad/box.scad>
include <./jl_scad/parts.scad>

module keyholePos() union() {
  back(5.9)
    contactPos();
  back(3.8)
    right(5)
      contactPos();
}

module contact_part() {
  contactPos();
  box_cut()
    contactHole();
}

module custom_hole(d) {
  p = hexagon(id = d);
  box_cutout(p);
}

module key_part() {
  box_half(TOP, inside = false) {
    custom_hole(3.2);
    xflip_copy()
      left(5.5)
        custom_hole(1.8);
    back(5.9)
      contact_part();
    back(3.8)
      right(5)
        contact_part();
  }
}

render()
  box_make(halves = [TOP])
    box_shell_base_lid([20, 20, 0], walls_outside = true, rim_height = 0, rtop = 0) {
      box_pos()
        //move(tile_size / 2)
        key_part();
    }
