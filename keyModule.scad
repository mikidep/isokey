include <prelude.scad>
use <contactModule156.scad>

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

key_module();
