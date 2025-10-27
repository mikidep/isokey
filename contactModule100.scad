include <BOSL2/std.scad>

EPSILON = 0.001;

module contact() import("./640636-3.off", convexity = 4);

SHEET_TH = 0.318;
CONTACT_H = 11.481;
HOLE_DEPTH = 1.6;
HOLE_H = 8.7;
HOLE_W = 1.9;
SHELL_TH = 0.8;

module contact_trans() down(CONTACT_H)
  xrot(180)
    children();

//contact_trans()
//  contact();

module contactHole() {
  up(0.001)
    back(SHEET_TH)
      diff()
        cube([HOLE_W, HOLE_DEPTH, HOLE_H], anchor = TOP + BACK) {
          edge_profile([TOP + LEFT, TOP + RIGHT])
            mask2d_chamfer(x = 0.4, y = 0.6);
          position(BACK + TOP)
            down(3)
              cube([1, 0.5, 2.5], anchor = TOP + FRONT);
        }
}

contactHole();

module contactPos() zscale(0.99)
  down(EPSILON)
    minkowski() {
      bounding_box()
        contactHole();
      cube([SHELL_TH, SHELL_TH, EPSILON], anchor = TOP);
    }

#contactPos();
