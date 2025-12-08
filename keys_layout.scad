include <prelude.scad>
use <./isolayout.scad>
use <keyModule.scad>
use <./pico.scad>

u = KKD * [1, 0];
v = KKD * [0.5, sqrt(3) / 2];
xi = KKD * [0.5, sqrt(3) / 6];

function u() =
  u;
function v() =
  v;
function xi() =
  xi;

function irect(cols, rows) =
  rect([u.x * cols - 0.1, v.y * rows - 0.2], anchor = BOTTOM + LEFT);

function keys_pts(cols, rows) =
  lattice_points(u, v, inside = irect(cols, rows));

function screw_pts(cols, rows) =
  let (ts = tiles_size(cols, rows), //
  pts = lattice_points(2 * u, 3 * v, inside = irect(cols - 1, rows)), //
  topptsdist = 2 * tile_size.x, //
  ntoppts = floor((ts.x - 2 * tile_size.x - pico_l()) / topptsdist), //
  toppts = [
    for (i = [0:ntoppts])
      [1.5 * tile_size.x + i * topptsdist, ts.y + pico_extra_h() * 3 / 4]
  ])
    concat(move(xi, pts), //
    move(-tile_size / 2, toppts));


tile = lattice_tile(u, v, xi);

function tile() =
  tile;

tile_size = pointlist_size(tile);

function tile_size() =
  tile_size;

function tiles_size(cols, rows) =
  pointlist_size(keys_pts(cols, rows)) + tile_size;
