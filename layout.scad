include <BOSL2/std.scad>

function applyM(M, points) =
  transpose(M * transpose(points));

u = [1, 0];
v = [0.3, 1];

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

for(xy = xys)
  translate(xy)
    circle(d = 0.5);
