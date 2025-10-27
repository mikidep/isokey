include <prelude.scad>
use <contactModule100.scad>
include <./jl_scad/box.scad>
include <./jl_scad/parts.scad>

module keyholeCutout() {
  back(5.9)
    contactHole();
  back(3.8)
    right(5)
      contactHole();
  cyl(d = 3.2 + 2 * $slop, h = 4, anchor = TOP);
  xflip_copy()
    left(5.5)
      cyl(d = 1.8 + 2 * $slop, h = 4, anchor = TOP);
}

module keyholePos() union() {
  back(5.9)
    contactPos();
  back(3.8)
    right(5)
      contactPos();
}


module key_module() difference() {
  union() {
    down(PTH)
      linear_extrude(PTH)
        hexagon(id = SP + EPSILON, realign = true);
    keyholePos();
  }
  zscale(1.01)
    up(0.01)
      keyholeCutout();
}

module contact_part() {
  contactPos();
  box_cut()
    contactHole();
}

module key_part() {
  box_half(TOP, inside = false) {
    box_hole(3.2);
    xflip_copy()
      left(5.5)
        box_hole(1.8);
    back(5.9)
      contact_part();
    back(3.8)
      right(5)
        contact_part();
  }
}
