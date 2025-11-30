include <BOSL2/std.scad>

EPSILON = 0.001;

module contact() import("./640636-3.off", convexity = 4);

SHEET_TH = 0.318;
CONTACT_H = 11.481;
HOLE_DEPTH = 1.8;
HOLE_H = 7.3;
HOLE_H2 = 8.7;
HOLE_W = 2.6;
HOLDER_Z = 5.5;
HOLE_W2 = 1.6;
SHELL_TH = 0.8;

module contactHoleCore() {
  module front_piece() cube([HOLE_W2, HOLE_DEPTH, HOLE_H], anchor = TOP + BACK);
  module back_piece() cube([HOLE_W, 1.5 * SHEET_TH, HOLE_H], anchor = TOP + BACK)
    position(BOTTOM + BACK)
      cube([HOLE_W, HOLE_DEPTH, HOLE_H2 - HOLE_H], anchor = TOP + BACK);

  render(convexity = 2)
    back(2 * SHEET_TH) {
      front_piece();
      back_piece();
      children();
    }
}

module contactHole() {
  contactHoleCore() {
    fwd(HOLE_DEPTH - EPSILON)
      extrude_from_to([-HOLE_W2 / 2, 0, 0], [HOLE_W2 / 2, 0, 0])
        yflip()
          right_triangle([2, SHELL_TH]);
    down(HOLDER_Z)
      fwd(EPSILON)
        cube([1, 2 * SHELL_TH, 2.5], anchor = BOT + FRONT);
  }
}

module contactPos() {
  TOPSIZE = [HOLE_W, HOLE_DEPTH] + 2 * [SHELL_TH, SHELL_TH];

  fwd(SHELL_TH / 2)
    prismoid(size1 = TOPSIZE, size2 = 2 * TOPSIZE, h = HOLE_H2, anchor = TOP);
}

difference() {
  contactPos();
  contactHole();
}
