include <prelude.scad>
use <./keys_layout.scad>
use <./keyModule.scad>
use <./pico.scad>

tile = tile();
u = u();
v = v();

BOX_TOP_TH = 2;
WALL_TH = 2;
BOX_H_OUT = 11.5;

module latticeModule(cols, rows) {
  kpts = [
    for (i = [0:cols - 1], j = [0:rows - 1])
      u * (i - floor(j / 2)) + v * j
  ];

  tileftp = union([
    for (p = kpts)
      move(p, tile)
  ]);

  linear_sweep(tileftp, -BOX_TOP_TH);

  wall_ftp = offset_stroke(tileftp, [-WALL_TH, 0], closed = true);
  %linear_sweep(wall_ftp, -BOX_H_OUT);

  module place_joints() {
    joinpt = (u() - v() - xi()) / 2;
    move(joinpt)
      children();
  }
  place_joints()
    cyl();

}


module mod() latticeModule(4, 4);

mod();

color("palegreen")
  move(4 * u)
    mod();

color("peachpuff")
  move(4 * v - 2 * u)
    mod();
color("powderblue")
  move(4 * v + 2 * u)
    mod();

