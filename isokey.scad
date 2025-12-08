include <prelude.scad>
use <./keys_layout.scad>
use <./keyModule.scad>
use <./pico.scad>


COLS = 6;
ROWS = 4;

tile = tile();
u = u();
v = v();

kpts = [
  for (i = [0:COLS - 1], j = [0:ROWS - 1])
    u * (i - floor(j / 2)) + v * j
];

tileftp = union([
  for (p = kpts)
    move(p, tile)
]);

linear_extrude(0.1)

  region(tileftp);

debug_pts(kpts);
