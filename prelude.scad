include <BOSL2/std.scad>
$fa = 1;
$fs = $preview ? 1 : 0.25;
$slop = 0.1;
EPSILON = 0.001;
PLATE_TH = 1.5;

KKD = 21.5; // Key to key distance

module debug_pt(pt, clr = "red") translate(pt)
  color(clr)
    sphere(r = 1);


module debug_pts(pts, clr = "red") for(pt = pts)
  debug_pt(pt, clr);

function bounds_to_size(bds) =
  bds[1] - bds[0];

function pointlist_size(pts) =
  bounds_to_size(pointlist_bounds(pts));
