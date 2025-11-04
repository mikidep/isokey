include <BOSL2/std.scad>

EPSILON = 0.001;

module contact() import("./640636-3.off", convexity = 4);

SHEET_TH = 0.318;
CONTACT_H = 11.481;
HOLE_DEPTH = 1.6;
HOLE_H = 8.7;
HOLE_W = 2.4;
HOLE_W2 = 1.8;
SHELL_TH = 1.2;

module contactHole() {
  module front_piece() cube([HOLE_W2, HOLE_DEPTH, HOLE_H], anchor = TOP + BACK)
    down(0.01)
      edge_profile(TOP + FRONT)
        xflip()
          mask2d_chamfer(x = 1, y = 2);

  module back_piece() diff()
    cube([HOLE_W, 1.5 * SHEET_TH, HOLE_H], anchor = TOP + BACK) {
      edge_profile([TOP + LEFT, TOP + RIGHT], excess = 0.001)
        let(cd = (HOLE_W - HOLE_W2) / 2)
          mask2d_chamfer(x = cd, y = 1.5 * cd);
      up(HOLE_H - 5.5)
        tag("keep")
          edge_profile(BOTTOM + BACK)
            xflip()
              mask2d_chamfer(x = 0.8, y = 3);
    }
  render()
    back(SHEET_TH) {
      up(0.001)
        front_piece();
      back_piece();
    }
}


module contactPos() render()
  zscale(0.99)
    down(EPSILON)
      minkowski() {
        bounding_box()
          contactHole();
        cube([SHELL_TH, SHELL_TH, EPSILON], anchor = TOP);
      }

module contact_trans() back(SHEET_TH)
  down(CONTACT_H)
    xrot(180)
      children();

//contact_trans()
//  contact();

//#contactHole();

difference() {
  contactPos();
  contactHole();
}
