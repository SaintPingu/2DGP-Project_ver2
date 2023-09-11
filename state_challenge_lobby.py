from tools import *
import framework
import state_lobby
import state_battle
import sound
import inventory

_background : Image

_buttons : dict
_font : Font

_images : list
_image_inventory : Image
_image_item_double : Image
_image_item_extension : Image
_image_item_heal : Image
_inven_item : inventory.Inven_Item
_inven_item_enemy : inventory.Inven_Item

_my_items = { 'double' }
_enemy_items = { 'double' }
_is_challenge = False
_challenge_level = 0

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
        if self.image:
            self.image.composite_draw(0, self.composite, *self.position)
    
    def check_select(self, point):
        if not point_in_rect(point, self.rect):
            return False
        
        sound.play_sound('click')

        if self.name == "home":
            global _is_challenge
            _is_challenge = False
            framework.change_state(state_lobby)
            return True
        elif self.name == "fight":
            framework.change_state(state_battle)
            return True
        
        return True

def enter():
    global _is_challenge
    _is_challenge = True

    global _background
    _background = load_image_path('challenge_back.png')

    # button images
    image_home = load_image_path('button_home.png')
    image_fight = load_image_path('button_fight.png')
    
    button_home = Button("home", image_home, (50, 950))
    button_fight = Button("fight", image_fight, (1280//2, 150))

    global _buttons
    _buttons = dict()
    _buttons[button_home.name] = button_home
    _buttons[button_fight.name] = button_fight

    global _font
    _font = load_font_path("DS-DIGIB", 60)

    global _image_inventory, _image_item_double, _image_item_extension, _image_item_heal
    #_image_inventory = load_image_path('inventory_item.png')
    _image_item_double = load_image_path('item_double.png')
    _image_item_extension = load_image_path('item_extension.png')
    _image_item_heal = load_image_path('item_heal.png')

    global _images
    _images = []
    #_images.append(_image_inventory)
    _images.append(_image_item_double)
    _images.append(_image_item_extension)
    _images.append(_image_item_heal)

    inventory.enter()
    global _inven_item, _inven_item_enemy
    _inven_item = inventory.Inven_Item((330, 350))
    _inven_item_enemy = inventory.Inven_Item((955, 350))

    for item in _my_items:
        _inven_item.add_item(item)
    
    for item in _enemy_items:
        _inven_item_enemy.add_item(item)

def exit():
    global _buttons
    for button in _buttons.values():
        button.release()
        del button
    _buttons.clear()
    del _buttons

    global _font
    del _font

    global _images
    for image in _images:
        del image
    del _images

    global _inven_item, _inven_item_enemy
    del _inven_item, _inven_item_enemy
    inventory.exit()

def draw():
    clear_canvas()
    _background.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    global _buttons
    for button in _buttons.values():
        button.draw()

    _font.draw(200, 550, "HP : 100", (255, 255, 255))
    _font.draw(825, 550, "HP : 150", (255, 255, 255))

    #_image_inventory.draw(330, 350)
    _inven_item.draw()
    _inven_item_enemy.draw()

    update_canvas()

def update():
    pass

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                point = convert_pico2d(event.x, event.y)
                for button in _buttons.values():
                    if button.check_select(point) == True:
                        break

def pause():
    pass
def resume():
    pass