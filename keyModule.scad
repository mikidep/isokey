include <prelude.scad>
use <contactModule100.scad>
use <./jl_scad/box.scad>
use <./jl_scad/parts.scad>
include <./jl_scad/prelude.scad>

module contact_part() {
  contactPos();
  box_cut()
    contactHole();
}

module custom_hole(d) {
  p = square([d, d], anchor = CENTER);
  box_cutout(p);
}

module key_part(side = TOP) {
  custom_hole(3.2);
  xflip_copy()
    left(5.5)
      custom_hole(1.5);
  back(5.9)
    contact_part();
  back(3.8)
    right(5)
      contact_part();
  fwd(5.9)
    left(3)
      zrot(90)
        contact_part();
}

render()
  box_make(halves = [TOP])
    box_shell_base_lid([20, 20, 0], walls_outside = true, rim_height = 0, rtop = 0) {
      box_pos()
        //move(tile_size / 2)
        key_part();
    }
