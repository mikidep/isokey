include <prelude.scad>
use <./keys_layout.scad>
use <./jl_scad/box.scad>
use <./keyModule.scad>
use <./pico.scad>
include <./jl_scad/prelude.scad>

tile_size = bounds_to_size(pointlist_bounds(tile()));
pts_size = bounds_to_size(pointlist_bounds(keys_pts()));
pico_size = bounds_to_size(pointlist_bounds(pico_ftp()));
box_size = tile_size + pts_size; // + [0, pico_size.y];

echo(box_size);

//rect(box_size);
render()
  box_make(halves = [TOP])
    box_shell_base_lid([box_size.x, box_size.y, 20]) {
      box_pos(FRONT + LEFT)
        move(tile_size / 2)
          for(p = keys_pts())
            move(p)
              key_part();
    }

//debug_pts(pts = keys_pts(), clr = "red");
