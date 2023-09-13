if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_battle
import state_challenge_lobby
import sound
import control

# global
NUM_OF_MAP = 5
_crnt_mode : str
_crnt_difficulty : str
crnt_map_index = 0
_image_maps : list
_position_map = (520, 450)
_font : Font

# images
_background : Image
_image_check : Image
_image_green_light : Image
_image_red_light : Image
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

        global _crnt_mode, _crnt_difficulty, _image_maps

        sound.play_sound('click')

        if self.name == "PVP":
            _crnt_mode = "PVP"
            set_check_pos()
        elif self.name == "PVE":
            _crnt_mode = "PVE"
            set_check_pos()
        elif self.name == "CHALLENGE":
            framework.change_state(state_challenge_lobby)
            return True
        elif self.name == "left":
            map.change(-1)
        elif self.name == "right":
            map.change(1)
        elif self.name == "start":
            if map.t == 0:
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
        return True
    


class SpriteSheet:
    def __init__(self, image, max_frame_row, max_frame_col, animation_interval):
        self.frame = 0
        self.image = image
        self.max_frame_row = max_frame_row
        self.max_frame_col = max_frame_col
        self.max_frame = max_frame_row * max_frame_col

        self.image_width = image.w // max_frame_col
        self.image_height = image.h // max_frame_row

        self.animation_called = 0
        self.animation_interval = animation_interval
    
    def draw(self, position):
        frame_x = 0 * self.image_width
        frame_y = 6 * self.image_height
        self.image.clip_draw(frame_x, frame_y, self.image_width, self.image_height, position[0], position[1])
    
    def animate(self):
        self.animation_called += 50 * framework.frame_time
        if self.animation_called >= self.animation_interval:
            self.animation_called = 0
            self.frame = (self.frame + 1) % self.max_frame
    
    def check_terminated(self):
        if self.animation_called == 0 and self.frame == 0:
            return True
        return False


class Effect():
    def __init__(self, sprite_sheet : SpriteSheet, position):
        self.sprite_sheet = sprite_sheet
        self.position = position
    
    def draw(self):
        self.sprite_sheet.draw(self.position)

    def animate(self):
        self.sprite_sheet.animate()
        if self.sprite_sheet.check_terminated():
            return False
        return True

effects = []

class MAP():
    def __init__(self):
        self.index = 0
        self.next_index = 0
        self.t = 0
        self.width = 520
        self.speed = 0.1
    
    def update(self):
        if self.index == self.next_index:
            return
        
        self.t += framework.frame_time * self.speed
        self.speed += framework.frame_time * 2
        if self.t >= 1:
            self.t = 0
            self.speed = 0.1
            self.index = self.next_index
            global crnt_map_index
            crnt_map_index = self.index
            if self.index == NUM_OF_MAP - 1:
                crnt_map_index = random.randint(0, NUM_OF_MAP + 1)
                if crnt_map_index >= NUM_OF_MAP:
                    crnt_map_index = NUM_OF_MAP - 1

    def draw_a(self, index, t1, t2):
        x = _position_map[0] - 520//2 + ((520//2) * t1)
        y = _position_map[1]
        _image_maps[index].clip_draw(0, 0, int(SCREEN_WIDTH * t1), SCREEN_HEIGHT, x, y, int(520 * t1), 500)
    
    def draw_b(self, index, t1, t2):
        x = _position_map[0] + 520//2 - ((520//2) * t2)
        y = _position_map[1]
        _image_maps[index].clip_draw(int(SCREEN_WIDTH * t1), 0, int(SCREEN_WIDTH * t2), SCREEN_HEIGHT, x, y, int(520 * t2), 500)

    def draw(self):
        if self.index == self.next_index:
            _image_maps[self.index].draw(*_position_map, 520, 500)
        else:
            if self.index < self.next_index:
                prev = self.index
                next = self.next_index
                t1 = 1 - self.t
                t2 = self.t
                self.draw_a(prev, t1, t2)
                self.draw_b(next, t1, t2)
                
                for i, effect in enumerate(effects):
                    t = i / len(effects)
                    y = _position_map[1] - _position_map[1]//2 + 500 * t
                    effect.position = (_position_map[0] + 520//2 - ((520) * t2), y)
            else:
                next = self.index
                prev = self.next_index
                t2 = 1 - self.t
                t1 = self.t
                self.draw_b(next, t1, t2)
                self.draw_a(prev, t1, t2)
                for i, effect in enumerate(effects):
                    t = i / len(effects)
                    y = _position_map[1] - _position_map[1]//2 + 500 * t
                    effect.position = (_position_map[0] + 520//2 - ((520) * t2), y)
            for effect in effects:
                effect.draw()
            

            

    def change(self, dir):
        if self.t != 0:
            return
        next_index = self.index + dir
        # if next_index < 0 or next_index >= len(_image_maps):
        #     return
        if next_index < 0:
            next_index = NUM_OF_MAP - 1
        elif next_index >= NUM_OF_MAP:
            next_index = 0
        
        self.next_index = next_index

    

map : MAP



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
    global _background, _image_check, _image_green_light, _image_red_light
    _background = load_image_path('lobby.png')
    _image_check = load_image_path('lobby_icon_check.png')
    _image_green_light = load_image_path('green_light.png')
    _image_red_light = load_image_path('red_light.png')

    # button images
    image_pvp = load_image_path('lobby_button_pvp.png')
    image_pve = load_image_path('lobby_button_pve.png')
    image_challenge = load_image_path('lobby_button_challenge.png')
    image_arrow = load_image_path('lobby_button_arrow.png')
    image_start = load_image_path('lobby_button_start.png')
    image_selection = load_image_path('lobby_button_selection.png')
    
    button_pvp = Button("PVP", image_pvp, (980, 750))
    button_pve = Button("PVE", image_pve, (980, 620))
    button_challenge = Button("CHALLENGE", image_challenge, (1000, 880))
    button_left = Button("left", image_arrow, (200, 450), 'h')
    button_right = Button("right", image_arrow, (200 + 630, 450))
    button_start = Button("start", image_start, (515, 100))
    button_easy = Button("easy", image_selection, (1010, 450))
    button_normal = Button("normal", image_selection, (1010, 450 - 100))
    button_hard = Button("hard", image_selection, (1010, 450 - 200))
    button_god = Button("god", image_selection, (1010, 450 - 300))

    global _buttons
    _buttons = dict()
    _buttons[button_pvp.name] = button_pvp
    _buttons[button_pve.name] = button_pve
    _buttons[button_challenge.name] = button_challenge
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
    for i in range(NUM_OF_MAP - 1):
        _image_maps.append(load_image_path("map_" + str(i + 1) + ".png"))
    _image_maps.append(load_image_path("map_random.png"))

    global map
    map = MAP()

    # set globals
    global _crnt_mode, crnt_map_index, _crnt_difficulty
    _crnt_mode = "PVP"
    _crnt_difficulty = "easy"
    crnt_map_index = 0
    set_check_pos()

    global _font
    _font = load_font_path("DS-DIGIB", 38)

    global effects
    effect_image = load_image_path('Impact.png')
    effect_sprite_sheet = SpriteSheet(effect_image, 8, 8, 5)
    for i in range(10):
        effects.append(Effect(effect_sprite_sheet, (0,0)))

    if sound._crnt_bgm_name != 'title':
        sound.play_bgm('title')
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

    for effect in effects:
        del effect
    effects.clear()

    global _image_green_light, _image_red_light
    del _image_green_light, _image_red_light

def update():
    map.update()

def draw():
    clear_canvas()
    _background.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    map.draw()

    start_x = 450
    for i in range(NUM_OF_MAP):
        if i != map.index:
            image = _image_red_light
        else:
            image = _image_green_light
        image.draw(start_x + i * 35, 180)



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
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                import state_title
                framework.change_state(state_title)

def get_mode():
    return _crnt_mode

def get_difficulty():
    return _crnt_difficulty

def pause():
    pass
def resume():
    pass