include <BOSL2/std.scad>

EPSILON = 0.001;

module contact() import("./640631-3.off", convexity = 4);

CONTACT_L = 10.18;
BACK_TH = 0.32;
HOLE_TH = 2.8;

module contactRel() bottom_half()
  up(6.0)
    contact();

module lance() front_half()
  back(EPSILON)
    contactRel();

module contactRelNoLance() {
  back_half()
    back(EPSILON)
      contactRel();
}

module ch_raw(withLance = true) {
  if (withLance)
    back(EPSILON)
      bounding_box()
        lance();

  bounding_box()
    front_half(y = 1)
      contactRelNoLance();

  resize([0, HOLE_TH, 0])
    bounding_box() {
      back_half(y = 1)
        contactRelNoLance();

      resize([EPSILON, 0, 0])
        contactRelNoLance();
    }
}

module contactHoleExact(withLance = true) xscale(1.1)
  yrot(180)
    fwd(BACK_TH)
      up(CONTACT_L)
        ch_raw(withLance);

module contactHole() up(2 * EPSILON)
  contactHoleExact();

module contactPos() {
  zscale(1 - 2 * EPSILON)
    minkowski() {
      contactHoleExact(withLance = false);
      wall = 0.8;
      cube([2 * wall, 2 * wall, EPSILON], anchor = TOP);
    }
}

contact();
// difference() {
//   contactPos();
//   contactHole();
// }
