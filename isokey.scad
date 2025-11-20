include <prelude.scad>
use <./keys_layout.scad>
use <./jl_scad/box.scad>
use <./jl_scad/parts.scad>
use <./keyModule.scad>
use <./muctrl.scad>
include <./jl_scad/prelude.scad>

keys_pts = keys_pts(5, 2);
tile = tile();

tiles_pts = flatten([
  for (p = keys_pts)
    move(p, tile)
]);
tile_size = bounds_to_size(pointlist_bounds(tile));
tiles_size = bounds_to_size(pointlist_bounds(tiles_pts));
box_size = tiles_size;

echo(box_size);

module mybox() box_shell_base_lid([box_size.x, box_size.y, 28], rtop = 6, rsides = 15, rim_height = 3, k = 0.5)
  children();

render()
  box_make(halves = [TOP, BOT], explode = 20)
    mybox() {
      box_half(TOP, inside = false)
        box_pos(FRONT + LEFT)
          move([2, 2] + tile_size / 2)
            for(p = keys_pts)
              move(p)
                key_part();
      box_half(BOT, inside = false)
        box_pos(BACK + LEFT)
          move([15, 30])
            key_part(side = BOT);
      position(RIGHT)
        left(30)
          mupart(5);

      up($box_rim_height)
        box_part([LEFT, RIGHT])
          box_snap_fit([5, 2], spring_len = 4, spring_dir = FRONT, thru_hole = false, depth = 0.6, spring_slot2 = 5);

    }

//debug_pts(pts = keys_pts(), clr = "red");
