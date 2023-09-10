if __name__ == "__main__":
    quit()

from tools import *
import framework
import object
import sound


MAX_AIR_DROP = 8

_is_supply : bool
_area = 0

class AirDrop(object.GroundObject):
    image : Image
    image_parachute : Image
    FALL_SPEED = get_pps(500)
    def __init__(self, center):
        from inventory import Inven_Item
        super().__init__(AirDrop.image, center, AirDrop.image.w, AirDrop.image.h)
        self.is_falling = True
        self.create()
        
        item_count = len(Inven_Item.items)
        self.item : str = Inven_Item.items[random.randint(0, item_count - 1)]
    
    def update(self):
        if self.is_falling:
            self.invalidate()
            self.fall()
            return
        
        self.invalidate()

    def draw(self):
        if self.is_falling:
            AirDrop.image_parachute.draw(*self.get_parachure_center())
        super().draw()
        
    def invalidate(self, is_invalidate_square=False, is_force=False, is_grid=False):
        super().invalidate(is_invalidate_square, is_force, is_grid)
        if self.is_falling:
            from gmap import resize_rect_inv, set_invalidate_rect
            rect_parachure = Rect(self.get_parachure_center(), AirDrop.image_parachute.w, AirDrop.image_parachute.h)
            resize_rect_inv(rect_parachure)
            set_invalidate_rect(*rect_parachure.__getitem__(), grid_size=0)
    
    def get_parachure_center(self):
        return self.center.x, self.center.y + (AirDrop.image_parachute.h//2 + AirDrop.image.h//2)

    def fall(self):
        global _is_supply
        from gmap import check_collision_vectors
        vec_bot = self.get_vectors_bot()
        center = self.center.x, self.center.y - (AirDrop.FALL_SPEED * framework.frame_time)
        self.set_center(center)
        self.invalidate(is_force=True)
        if check_collision_vectors(vec_bot) == True:
            self.is_falling = False
            self.rotate_ground(True, True)
            _is_supply = False
            sound.play_sound('crash')
            return
        
        from tank import get_tanks
        for tank in get_tanks():
            if check_collision(tank) == True:
                _is_supply = False
                return
        if self.center.y < MIN_HEIGHT:
            _is_supply = False
            delete_air_drop(self)
        
    def get_item(self):
        return self.item
            
class Ship(object.FlyObject):
    image : Image
    SUPPLY_POINT_X = 10
    def __init__(self):
        self.dir = random.randint(0, 1) * 2 - 1 # Left or Right

        image_flip = ''
        pos_x = -Ship.image.w * 2
        if self.dir == LEFT:
            image_flip = 'h'
            pos_x = SCREEN_WIDTH + Ship.image.w * 2
        
        yPos = random.randint(MAX_HEIGHT + Ship.image.h, SCREEN_HEIGHT - Ship.image.h)
        
        super().__init__(Ship.image, (pos_x, yPos), Ship.image.w, Ship.image.h, dir=self.dir, image_flip=image_flip)

        self.speed = get_pps(1000)

        global _area
        if _area == LEFT:
            self.drop_pos_x = random.randint(100, SCREEN_WIDTH //2)
        else:
            self.drop_pos_x = random.randint(SCREEN_WIDTH //2, SCREEN_WIDTH - 100)
        _area *= -1

        self.is_droped = False
        self.is_move = False

    def update(self):
        if self.is_move == False:
            return

        self.invalidate()
        self.move()

        is_destroy = False
        if self.dir == LEFT:
            if self.center.x <= -self.image.w:
                is_destroy = True
            elif self.center.x <= self.drop_pos_x:
                self.drop_item()
        elif self.dir == RIGHT:
            if self.center.x >= SCREEN_WIDTH + self.image.w:
                is_destroy = True
            elif self.center.x >= self.drop_pos_x:
                self.drop_item()

        if is_destroy:
            delete_ship()
            return False
        
        self.invalidate(is_force=True)
        return True

    def drop_item(self):
        if self.is_droped == False:
            create_air_drop((self.drop_pos_x + (Ship.SUPPLY_POINT_X * self.dir), self.center.y - self.height//2))
            self.is_droped = True
            sound.play_sound('parachute')




_air_drops : list[AirDrop]
_ship : Ship
_crnt_drop : AirDrop = None

def enter():
    Ship.image = load_image_path('drop_ship.png')
    AirDrop.image = load_image_path('air_drop.png')
    AirDrop.image_parachute = load_image_path('air_drop_parachute.png')

    global _ship
    _ship = None
    
    global _air_drops, _is_supply
    _air_drops = []
    _is_supply = False

    global _area
    _area = random.randint(0, 1) * 2 - 1    # LEFT or RIGHT

def exit():
    del Ship.image
    del AirDrop.image
    del AirDrop.image_parachute

    global _air_drops
    _air_drops.clear()
    del _air_drops

def update():
    if _ship != None:
        if _ship.is_move == False:
            sound.play_sound("air_ship")
            _ship.is_move = True
    return _is_supply

def draw():
    pass

def reset():
    create_ship()

def create_ship():
    global _ship, _is_supply
    if _ship != None:
        return
    if _is_supply:
        return

    _ship = Ship()
    object.add_object(_ship)
    _is_supply = True

    global _air_drops
    if len(_air_drops) >= MAX_AIR_DROP:
        air_drop = _air_drops[0]
        delete_air_drop(air_drop)

def delete_ship():
    global _ship, _is_reseted
    if _ship == None:
        return

    object.delete_object(_ship)
    _ship = None
    _is_reseted = False

def create_air_drop(position):
    global _crnt_drop

    _crnt_drop = AirDrop(position)
    object.add_object(_crnt_drop)
    _air_drops.append(_crnt_drop)

def delete_air_drop(air_drop):
    global _air_drops
    assert(air_drop in _air_drops)

    object.delete_object(air_drop)
    _air_drops.remove(air_drop)
    air_drop = None


def check_collision(object : object.GroundObject):
    rect_object = object.get_square()
    for air_drop in _air_drops:
        distance_x = math.fabs(object.center.x - air_drop.center.x)
        if distance_x > (object.width/2 + air_drop.width/2):
            continue

        air_drop_rect = air_drop.get_square()
        if air_drop_rect.collide_rect(rect_object) == True:
            object.add_item(air_drop.get_item())
            delete_air_drop(air_drop)
            sound.play_sound('pickup_item')
            return True
    
    return False