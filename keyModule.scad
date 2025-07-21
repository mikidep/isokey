include <prelude.scad>

module keyholeCutout()
{
    back(5.9) contactHole();
    back(3.8) right(5) contactHole();
    cyl(d = 3.2 + 2 * $slop, h = 4, anchor = TOP);
    xflip_copy() left(5.5) cyl(d = 1.8 + 2 * $slop, h = 4, anchor = TOP);
}

module keyholePos() union()
{
    back(5.9) bbox() contactHole();
    back(3.8) right(5) bbox() contactHole();
}

module contactHole()
{
    let(bs = 1.7 + 2 * $slop) cube([ bs, bs, 7 ], anchor = TOP) position(BOTTOM) let(bs = 1.8 + 2 * $slop)
        cube([ bs, bs, 1.5 ], anchor = BOTTOM);
}

module key_module() difference()
{
    union()
    {
        down(PTH) linear_extrude(PTH) hexagon(id = SP + $eps, realign = true);
        keyholePos();
    }
    zscale(1.01) up(0.01) keyholeCutout();
}

// key_module();
contactHole();
