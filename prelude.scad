include <BOSL2/std.scad>
$fn = 20;
$slop = 0.1;
EPSILON = 0.001;

HW = 20.96;
SP = 21.5;
KBU = 13.8;
PTH = 2; // Plate thickness

module bbox() intersection() {
  bounding_box(1) children();
  scale([ 100, 100, 1 ]) bounding_box() children();
}

