include <BOSL2/std.scad>

function applyM(M, points) =
  transpose(M * transpose(points));

function base_change_2d(u, v, inverse = false) =
  let (UV = hstack(u, v)) //
    function(points) //
    applyM(inverse ? UV : matrix_inverse(UV), points);

function lattice_points(u, v, inside) =
  let ( //
  xy_uv = base_change_2d(u, v), //
  uv_xy = base_change_2d(u, v, inverse = true), //
  uvshape = xy_uv(inside), //
  uvbounds = pointlist_bounds(uvshape), //
  umin = uvbounds[0][0], //
  vmin = uvbounds[0][1], //
  umax = uvbounds[1][0], //
  vmax = uvbounds[1][1], //
  mask = offset(uvshape, 0.01), //
  uvs = [
    for (u = [umin:umax], v = [vmin:vmax])
      if (point_in_region([u, v], mask) > 0)
        [u, v]
  ], //
  xys = uv_xy(uvs) //
  )
    xys;

function lattice_tile(u, v, xi) =
  let ( //
  uv_xy = base_change_2d(u, v, inverse = true), //
  xy_uv = base_change_2d(u, v, inverse = false), //
  X = [1, 0], //
  Y = [0, 1], //
  xi_ = xy_uv([xi])[0], //
  uvtile = [xi_, X - xi_, xi_ - Y, -xi_, xi_ - X, Y - xi_] //
  )
    uv_xy(uvtile);


