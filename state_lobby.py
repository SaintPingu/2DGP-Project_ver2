if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_battle
import sound

# global
NUM_OF_MAP = 4
_crnt_mode : str
_crnt_difficulty : str
crnt_map_index = 0
_image_maps : list
_position_map = (520, 450)
_font : Font

# images
_background : Image
_image_check : Image
_check_pos_mode : tuple
_check_pos_diff : tuple

# buttons
_buttons : dict

class Button:
    def __init__(self, name : str, image : Image, position, composite = ''):
        self.name = name
        self.image : Image = image
        self.position = position
        self.rect = Rect(position, image.w, image.h)
        self.composite = composite
    
    def release(self):
        if self.image:
            del self.image
        del self.rect

    def draw(self):
        self.image.composite_draw(0, self.composite, *self.position)

        global _font
        if self.name == "easy":
            _font.draw(self.position[0] - 30, self.position[1], "EASY", (0, 204, 102))
        elif self.name == "normal":
            _font.draw(self.position[0] - 40, self.position[1], "NORMAL", (255, 128, 0))
        elif self.name == "hard":
            _font.draw(self.position[0] - 30, self.position[1], "HARD", (204, 0, 0))
        elif self.name == "god":
            _font.draw(self.position[0] - 30, self.position[1], "GOD", (0, 204, 204))

    
    def check_select(self, point):
        if not point_in_rect(point, self.rect):
            return False

        global _crnt_mode, crnt_map_index, _crnt_difficulty, _image_maps

        if self.name == "PVP":
            _crnt_mode = "PVP"
            set_check_pos()
        elif self.name == "PVE":
            _crnt_mode = "PVE"
            set_check_pos()
        elif self.name == "left":
            crnt_map_index -= 1
        elif self.name == "right":
            crnt_map_index += 1
        elif self.name == "start":
            sound.stop_bgm()
            framework.change_state(state_battle)
            sound.play_sound('click')
            return True
        elif self.name == "easy" or self.name == "normal" or self.name == "hard" or self.name == "god":
            if _crnt_mode == "PVE":
                _crnt_difficulty = self.name
                set_check_pos()
        else:
            assert(0)

        crnt_map_index = clamp(0, crnt_map_index, len(_image_maps) - 1)

        sound.play_sound('click')
        return True
    
def set_check_pos():
    global _crnt_mode, _check_pos_mode, _check_pos_diff
    if _crnt_mode == "PVP" or _crnt_mode == "PVE":
        _check_pos_mode = (_buttons[_crnt_mode].position[0] - 95, _buttons[_crnt_mode].position[1])
        if _crnt_mode == "PVE":
            _check_pos_diff = (_buttons[_crnt_difficulty].position[0] - 75,  _buttons[_crnt_difficulty].position[1] + 10)
    else:
        assert(0)





def enter():
    # images
    global _background, _image_check
    _background = load_image_path('lobby.png')
    _image_check = load_image_path('lobby_icon_check.png')

    # button images
    image_pvp = load_image_path('lobby_button_pvp.png')
    image_pve = load_image_path('lobby_button_pve.png')
    image_arrow = load_image_path('lobby_button_arrow.png')
    image_start = load_image_path('lobby_button_start.png')
    image_selection = load_image_path('lobby_button_selection.png')
    
    button_pvp = Button("PVP", image_pvp, (980, 750))
    button_pve = Button("PVE", image_pve, (980, 620))
    button_left = Button("left", image_arrow, (200, 450), 'h')
    button_right = Button("right", image_arrow, (200 + 630, 450))
    button_start = Button("start", image_start, (515, 125))
    button_easy = Button("easy", image_selection, (1010, 450))
    button_normal = Button("normal", image_selection, (1010, 450 - 100))
    button_hard = Button("hard", image_selection, (1010, 450 - 200))
    button_god = Button("god", image_selection, (1010, 450 - 300))

    global _buttons
    _buttons = dict()
    _buttons[button_pvp.name] = button_pvp
    _buttons[button_pve.name] = button_pve
    _buttons[button_left.name] = button_left
    _buttons[button_right.name] = button_right
    _buttons[button_start.name] = button_start
    _buttons[button_easy.name] = button_easy
    _buttons[button_normal.name] = button_normal
    _buttons[button_hard.name] = button_hard
    _buttons[button_god.name] = button_god

    # map images
    global _image_maps
    _image_maps = []
    for i in range(NUM_OF_MAP):
        _image_maps.append(load_image_path("map_" + str(i + 1) + ".png"))

    # set globals
    global _crnt_mode, crnt_map_index, _crnt_difficulty
    _crnt_mode = "PVP"
    _crnt_difficulty = "easy"
    crnt_map_index = 0
    set_check_pos()

    global _font
    _font = load_font_path("DS-DIGIB", 38)

    sound.add_sound('click')

def exit():
    global _buttons
    for button in _buttons.values():
        button.release()
        del button
    _buttons.clear()
    del _buttons

    global _image_maps
    _image_maps.clear()
    del _image_maps

    global _image_check
    del _image_check

    global _font
    del _font

def update():
    pass

def draw():
    clear_canvas()
    _background.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    _image_maps[crnt_map_index].draw(*_position_map, 520, 500)

    global _buttons
    for button in _buttons.values():
        button.draw()

    _image_check.draw(*_check_pos_mode)
    if _crnt_mode == "PVE":
        _image_check.draw(*_check_pos_diff)
    
    update_canvas()


def handle_events():
    global _crnt_mode, crnt_map_index, _buttons

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN:
            sound._crnt_bgm.resume()
            if event.button == SDL_BUTTON_LEFT:
                point = convert_pico2d(event.x, event.y)
                for button in _buttons.values():
                    if button.check_select(point) == True:
                        break


def get_mode():
    return _crnt_mode

def get_difficulty():
    return _crnt_difficulty

def pause():
    pass
def resume():
    pass