include <prelude.scad>
use <./keys_layout.scad>
include <./jl_scad/box.scad>
include <./jl_scad/parts.scad>
use <./keyModule.scad>
use <./pico.scad>

tile_size = bounds_to_size(pointlist_bounds(tile()));
pts_size = bounds_to_size(pointlist_bounds(keys_pts()));
pico_size = bounds_to_size(pointlist_bounds(pico_ftp()));
box_size = tile_size + pts_size + [0, pico_size.y];

//rect(box_size);



//box_make(explode = 30)
//  box_shell_base_lid([60, 20, 20]) {
//    key_part();
//    xmove(20)
//      key_part();
//  }
