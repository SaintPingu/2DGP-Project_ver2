if __name__ == "__main__":
    quit()

from tools import *
import gmap
import framework

SPRITES : set

def enter():
    global SPRITES
    img_sprite_shot = load_image_path('sprite_shot.png')
    img_sprite_explosion = load_image_path('sprite_explosion.png')
    img_sprite_explosion_nuclear = load_image_path('sprite_explosion_nuclear.png')
    img_sprite_tank_explosion = load_image_path('sprite_tank_explosion.png')
    SPRITES = {
        "Shot" : img_sprite_shot,
        "Explosion" : img_sprite_explosion,
        "Explosion_Nuclear" : img_sprite_explosion_nuclear,
        "Tank_Explosion" : img_sprite_tank_explosion 
    }

def exit():
    global SPRITES, animations
    for image in SPRITES.values():
        del image
    del SPRITES

    for animation in animations:
        del animation
    animations.clear()

def update():
    for animation in animations:
        if animation.update() is False:
            animations.remove(animation)

def draw():
    for animation in animations.__reversed__():
        animation.draw()

class Sprite:
    def __init__(self, sprite_name:str, position, max_frame:int, frame_width:int, frame_height:int, action_per_time : float, theta=0, max_frame_col:int = 1, scale=1, repeat_count=1):
        assert sprite_name in SPRITES.keys()

        self.sprite : Image = SPRITES[sprite_name]
        self.max_frame = max_frame
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame = 0
        self.position = position
        self.repeat_count = repeat_count
        self.theta = theta
        self.scale = scale
        self.max_frame_col = max_frame_col
        self.frame_row = 0

        self.action_per_time = action_per_time

        self.raidus = 0
        if self.frame_width > self.frame_height:
            self.raidus = self.frame_width*self.scale
        else:
            self.raidus = self.frame_height*self.scale

        if max_frame_col == 1:
            self.origin = Vector2(0, self.sprite.h)
        else:
            self.origin = Vector2(0, frame_height)

        self.origin.y = self.sprite.h - self.origin.y
    
    def set_action_per_time(value):
        pass

    def draw(self):
        from tank import check_invalidate
        frame = int(self.frame)
        
        left = 0
        bottom = 0
        if self.max_frame_col > 1:
            frame_row = int(self.frame) // self.max_frame_col
            left = self.origin.x + ((frame - (self.max_frame_col * frame_row)) * self.frame_width) 
            bottom = self.origin.y - (frame_row * self.frame_height)
        else:
            left = self.origin.x + (frame * self.frame_width) 
            bottom = self.origin.y

        if self.theta != 0:
            self.sprite.clip_composite_draw(left, bottom, self.frame_width, self.frame_height, self.theta, '', *self.position, self.frame_width//2 * self.scale, self.frame_height//2 * self.scale)
        else:
            self.sprite.clip_draw(left, bottom, self.frame_width, self.frame_height, *self.position, self.frame_width*self.scale, self.frame_height*self.scale)

        check_invalidate(self.position, self.raidus)

    def update(self):
        is_running = True

        self.frame += (self.max_frame * self.action_per_time * framework.frame_time)
        if self.frame >= self.max_frame:
            self.repeat_count -= 1
            if self.repeat_count <= 0:
                is_running = False
            else:
                self.frame -= self.max_frame

        inv_width = self.frame_width*self.scale
        inv_height = self.frame_height*self.scale
        gmap.set_invalidate_rect(self.position, inv_width, inv_height, square=True)
        
        return is_running
    
animations : list[Sprite] = []

def add_animation(sprite_name : Sprite, center, theta=0, scale=1.0):
    assert sprite_name in SPRITES.keys()

    sprite = None
    if sprite_name == "Shot":
        sprite = Sprite(sprite_name, center, 4, 30, 48, 1.5, theta, scale=scale)
    elif sprite_name == "Explosion":
        sprite = Sprite(sprite_name, center, 14, 75, 75, 1.0, max_frame_col=4, scale=scale)
    elif sprite_name == "Explosion_Nuclear":
        sprite = Sprite(sprite_name, center, 10, 58, 54, 0.5, max_frame_col=5, scale=scale)
    elif sprite_name == "Tank_Explosion":
        sprite = Sprite(sprite_name, center, 15, 65, 60, 0.5, max_frame_col=5, scale=scale)

    animations.append(sprite)