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

module mybox() box_shell_base_lid([box_size.x, box_size.y, 20], rtop = 6, rbot = 6, rsides = 15, rim_height = 3, k = 0.5)
  children();

module main() box_make(halves = [BOT], explode = 20)
  mybox() {
    box_half(TOP, inside = false)
      box_pos(FRONT + LEFT)
        move([2, 2] + tile_size / 2)
          for(p = keys_pts)
            move(p)
              key_part();
    box_half(BOT, inside = false)
      box_pos(BACK + LEFT)
        move([30, 30])
          key_part(side = BOT);
    mupart(8);

    up($box_rim_height)
      box_part([LEFT, RIGHT])
        box_snap_fit([5, 2], spring_len = 4, spring_dir = FRONT, thru_hole = false, depth = 0.6, spring_slot2 = 5);

  }

intersection() {
  main();
//right(47)
//  cube([30, 20, 24], anchor = CENTER);
}
