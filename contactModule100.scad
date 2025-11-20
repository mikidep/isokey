include <BOSL2/std.scad>

EPSILON = 0.001;

module contact() import("./640636-3.off", convexity = 4);

SHEET_TH = 0.318;
CONTACT_H = 11.481;
HOLE_DEPTH = 1.8;
HOLE_H = 7;
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
  //#down(HOLE_H2 + EPSILON)
  //  back(SHELL_TH + EPSILON)
  //    cube([0.7 * HOLE_W, HOLE_DEPTH + 2 * SHELL_TH + 2 * EPSILON, 2.8], anchor = BOT + BACK);
  }
}


module contactPos() render()
  zscale(0.99)
    down(EPSILON)
      minkowski() {
        bounding_box()
          contactHoleCore();
        cube([2 * SHELL_TH, 2 * SHELL_TH, EPSILON], anchor = TOP);
      }

module contact_trans() back(SHEET_TH)
  down(CONTACT_H)
    xrot(180)
      children();

difference() {
  contactPos();
  contactHole();
}
