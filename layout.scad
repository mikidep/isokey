include <BOSL2/std.scad>

$fn = 100;
function applyM(M, points) =
  transpose(M * transpose(points));

u = [1, 0];
v = [0.3, 1];

xi = [0.4, 0.2];

shape = move([-EPSILON, -EPSILON], rect([20, 10]));
UV = hstack(u, v);
UVinv = matrix_inverse(UV);

uv_xy = function(points)applyM(UV, points);
xy_uv = function(points)applyM(UVinv, points);

uvshape = xy_uv(shape);
uvbounds = pointlist_bounds(uvshape);
umin = uvbounds[0][0];
vmin = uvbounds[0][1];
umax = uvbounds[1][0];
vmax = uvbounds[1][1];
uvs = [
  for (u = [umin:umax], v = [vmin:vmax])
    if (point_in_region([u, v], uvshape) > 0)
      [u, v]
];
xys = uv_xy(uvs);

uvtile = let (X = [1, 0], Y = [0, 1])
  [xi, X - xi, xi - Y, -xi, xi - X, Y - xi];
xytile = uv_xy(uvtile);

for(xy = xys)
  translate(xy) {
    color("red")
      circle(d = 0.1);
    scale(0.95)
      region(xytile);
  }

