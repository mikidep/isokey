include <prelude.scad>
use <./isolayout.scad>
use <keyModule.scad>

u = KKD * [1, 0];
v = KKD * [0.5, sqrt(3) / 2];
xi = KKD * [0.5, sqrt(3) / 6];
function keys_pts(cols, rows) =
  let (irect = rect([u.x * cols - 0.2, v.y * rows - 0.2], anchor = BOTTOM + LEFT) //
  )
    lattice_points(u, v, inside = irect);

function tile() =
  lattice_tile(u, v, xi);
