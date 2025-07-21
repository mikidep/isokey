include <BOSL2/distributors.scad>
include <prelude.scad>

use <keyModule.scad>

CSCRWD = 3;           // Case screw diameter
CINSRD = 4;           // Case insert diameter
CINSRH = 4;           // Case insert height
BSCRWD = 2;           // Board screw diameter
BINSRD = 3;           // Board insert diameter
BINSRH = 4;           // Board insert height
TCSCRWHH = 5;         // Top case screwhole height
CSCRWHD = CINSRD + 3; // Case screwhole diameter (including support)
RNDNG = 8;
COLS = 12;
ROWS = 6;
WTH = 2; // Wall thickness
WH = 15; // Wall height

hexpts = grid_copies(spacing = SP, n = [ 2 * COLS, ROWS ], stagger = true, p = CENTER);
// boltpts = concat(right(SP / 2, [for (i = [12:5:len(hexpts) - 12])
// hexpts[i]]),
//        fwd(0.6 * SP, [for (i = [ 0, 4, 8, 11 ]) hexpts[i]]),
//        back(0.6 * SP, [for (i = [ 0, 4, 8, 11 ]) hexpts[60 + i]]),
//        left(SP / 2, [for (i = [ 24, 48 ]) hexpts[i]]));
boltpts = [];

module hexgrid()
{
    move_copies(hexpts) children();
}

module boltgrid()
{
    move_copies(boltpts) children();
}

module plate_2d()
{
    union() hexgrid() hexagon(id = SP + $eps, realign = true);
}

module walls()
{
    linear_extrude(WH) shell2d(thickness = -WTH) plate_2d();
}

module bot_screwhole() diff() cyl(d = CSCRWHD, h = WH - TCSCRWHH, anchor = BOTTOM) tag("remove") up(0.001) position(TOP)
    cyl(d = CINSRD, h = CINSRH, anchor = TOP);

module bottom() union()
{
    linear_extrude(PTH) plate_2d();
    up(PTH - 0.001)
    {
        walls();
        boltgrid() bot_screwhole();
    }
}

module top_plate()
{
    hexgrid() render() key_module();
}

module top_plate_()
{
}

// bottom();
// up(10) up(PTH + WH) top_plate();
top_plate();

module pico() import("Raspberry Pi Pico-R004.amf", convexity = 3);
