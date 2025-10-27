include <prelude.scad>
use <./isolayout.scad>
use <keyModule.scad>

//COLS = 12;
//ROWS = 6;

COLS = 6;
ROWS = 6;

u = KKD * [1, 0];
v = KKD * [0.5, sqrt(3) / 2];
xi = KKD * [0.5, sqrt(3) / 6];

irect = rect([ //
u.x * COLS - 0.2, //
v.y * ROWS - 0.2 //
], anchor = BOTTOM + LEFT);

pts = lattice_points(u, v, inside = irect);

tile = lattice_tile(u, v, xi);
tiles = [
  for (pt = pts)
    move(pt, tile)
];
tilebds = pointlist_bounds(tile);

keys_ftp = ymove(-tilebds[0].y, union([
  for (tile = tiles)
    scale(1 + EPSILON, tile)
]));

function keys_ftp() =
  keys_ftp;

function keys_pts() =
  pts;

function tile() =
  tile;
