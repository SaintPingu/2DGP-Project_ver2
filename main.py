from tools import *
import framework
import state_title

open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT, sync=True)
framework.run(state_title)
close_canvas()