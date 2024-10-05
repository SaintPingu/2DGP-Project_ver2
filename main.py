from tools import *
import framework
import state_title

os.chdir(os.path.dirname(__file__))
import control
if __name__ == '__main__':
    control.start()

    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT, sync=True)
    framework.run(state_title)
    close_canvas()
    control.end()