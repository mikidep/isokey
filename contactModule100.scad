include <BOSL2/std.scad>
use <./jl_scad/box.scad>
use <./jl_scad/parts.scad>

EPSILON = 0.001;

module contact() import("./640636-3.off", convexity = 4);

SHEET_TH = 0.318;
CONTACT_H = 11.481;
HOLE_DEPTH_SHEET = 1.5 * SHEET_TH;
HOLE_DEPTH = 1.8;
HOLE_DEPTH_HDR = 2;
HOLE_H = 7.3;
HOLE_H2 = 8.7;
HOLE_W = 3;
HOLDER_Z = 5.5;
HOLE_W2 = 1.4;
SHELL_TH = 0.8;

module contactHole(blade = true) {
  depth = blade ? HOLE_DEPTH : HOLE_DEPTH_HDR;

  module front_piece() cube([HOLE_W2, depth, HOLE_H], anchor = TOP + BACK);
  module back_piece() cube([HOLE_W, HOLE_DEPTH_SHEET, HOLE_H], anchor = TOP + BACK)
    position(BOTTOM + BACK)
      cube([HOLE_W, depth, HOLE_H2 - HOLE_H], anchor = TOP + BACK);

  up(EPSILON)
    zscale(1 + EPSILON)
      back(depth / 2) {
        front_piece();
        back_piece();
        fwd(depth - EPSILON)
          extrude_from_to([-HOLE_W2 / 2, 0, 0], [HOLE_W2 / 2, 0, 0])
            yflip()
              right_triangle([2, SHELL_TH]);
        down(HOLDER_Z)
          fwd(EPSILON)
            cube([1, 3 * SHELL_TH, 2.5], anchor = BOT + FRONT);
      }
}

module contactPos() {
  TOPSIZE = [HOLE_W, HOLE_DEPTH] + 2 * [SHELL_TH, SHELL_TH];

  prismoid(size1 = TOPSIZE, size2 = 1.8 * TOPSIZE, h = HOLE_H2, anchor = TOP);
}

module contact_part(blade = true) {
  contactPos();
  box_cut()
    contactHole(blade = blade);
}

module idc_tool() {
  h = 5;
  diff()
    rect_tube(h = h, isize = [HOLE_W, HOLE_DEPTH], wall = 2) {
      position(BOT)
        color("green")
          cube([0.8, HOLE_W, h], anchor = BOT);
      position(TOP)
        tag("remove")
          yrot(45)
            cube([1, 6, 1], anchor = CENTER);
    }


}

//difference() {
//  contactPos();
//  contactHole();
//}

//up(4)
//  contact();

idc_tool();
