if __name__ == "__main__":
    quit()

from tools import *
import framework

class GameObject:
    def __init__(self, center=(0,0), width=0, height=0, theta=0, dir=0):
        self.center : Vector2 = Vector2(*center)
        self.width : float = width
        self.height : float = height

        self.theta : float = theta
        self.is_rect_invalid : bool = True
        self.is_created : bool = False

        self.dir : int = dir
        self.speed : float = 1

        self.is_draw = True

        detect_square = self.get_square()
        self.detect_radius = (Vector2(*detect_square.center) - Vector2(detect_square.left, detect_square.top)).get_norm()
    
    def release(self):
        pass

    # update based on center, width, height, theta
    def update_object(self):
        self.is_rect_invalid = False

    def rotate(self, theta):
        self.theta += theta
        self.update_object()

    def set_theta(self, theta):
        if self.theta == theta:
            return
        self.theta = theta
        self.update_object()

    def rotate_pivot(self, theta, pivot):
        center = self.center
        self.center = center.get_rotated_pivot(pivot, theta)
        self.theta = theta
        self.update_object()

    def offset(self, dx, dy):
        self.center.x += dx
        self.center.y += dy
        self.update_object()

    def set_center(self, center):
        self.center.x = center[0]
        self.center.y = center[1]
        self.update_object()

    def draw_image(self, image : Image, scale = 1, flip=''):
        if self.is_rect_invalid == False:
            return
        self.is_rect_invalid = False
        image.composite_draw(self.theta, flip, *self.center, image.w*scale, image.h*scale)

    def get_rect(self):
        return Rect(tuple(self.center), self.width, self.height)
    
    def get_square(self):
        width = self.width
        height = self.height
        if width < height:
            width = height
        else:
            height = width
        return Rect(self.center, width, height)
    
    def out_of_bound(self, left= -9999, top= -9999, right= -9999, bottom= -9999):
        rect = self.get_rect()

        if left != -9999 and rect.left < left:
            return True
        elif top != -9999 and rect.top > top:
            return True
        elif right != -9999 and rect.right > right:
            return True
        elif bottom != -9999 and rect.bottom < bottom:
            return True

        return False

    def set_pos(self, center):
        self.set_center(center)
    
    def is_in_radius(self, position : Vector2, radius):
        distance = (position - self.center).get_norm()
        if distance < self.detect_radius + radius:
            return True

    def resize(self, scale : float):
        self.width *= scale
        self.height *= scale
        rect = self.get_rect()
        self.center.x = rect.origin[0] + self.width//2
        self.center.y = rect.origin[1] + self.height//2
        self.update_object()

    def toggle_show(self):
        self.is_draw = not self.is_draw

    def draw(self):
        pass
    
    def update(self):
        pass
    
    def invalidate(self, is_invalidate_square=False, is_force=False, is_grid=True):
        if is_force or self.is_rect_invalid == False:
            import gmap

            if is_invalidate_square:
                inv_rect = self.get_square()
            else:
                inv_rect = self.get_rect()
            gmap.resize_rect_inv(inv_rect)
            
            if is_grid==False:
                gmap.set_invalidate_rect(*inv_rect.__getitem__(), grid_size=0)
            else:
                gmap.set_invalidate_rect(*inv_rect.__getitem__())

            self.is_rect_invalid = True



import gmap
class GroundObject(GameObject):
    def __init__(self, image : Image, center=(0, 0), width=0, height=0, theta=0, image_flip=''):
        self.image = image

        super().__init__(center, width, height, theta)
        self.bot_left = Vector2()
        self.bot_right = Vector2()
        self.top_left = Vector2()
        self.top_right = Vector2()
        self.bot_center = Vector2()
        self.speed = 1
        self.image_flip = image_flip

        self.update_object()
    
    def release(self):
        self.invalidate(is_force=True)
    
    def draw(self):
        self.draw_image(self.image, flip=self.image_flip)

    def update_object(self):
        self.bot_left.x = self.top_left.x = self.center.x - self.width//2
        self.bot_left.y = self.bot_right.y = self.center.y - self.height//2
        self.bot_right.x = self.top_right.x = self.center.x + self.width//2
        self.top_left.y = self.top_right.y = self.center.y + self.height//2
        
        self.bot_left = self.bot_left.get_rotated_pivot(self.center, self.theta)
        self.bot_right = self.bot_right.get_rotated_pivot(self.center, self.theta)
        self.top_left = self.top_left.get_rotated_pivot(self.center, self.theta)
        self.top_right = self.top_right.get_rotated_pivot(self.center, self.theta)

        vec_left_to_center = (self.bot_right - self.bot_left).normalized() * (self.width // 2)
        self.bot_center = self.bot_left + vec_left_to_center
        super().update_object()
    
    def create(self):
        self.is_created = True
    
    def get_vec_left(self):
        return (self.bot_left - self.bot_right).normalized()
    def get_vec_right(self):
        return (self.bot_right - self.bot_left).normalized()

    def get_normal(self):
        return self.get_vec_right().get_rotated(math.pi/2)

    # t = 0 ~ 0.5
    def get_vectors_bot(self, t=0, max_t=1):
        return gmap.get_vectors(self.bot_left, self.bot_right, t, max_t)
    
    def get_vectors_top(self, t=0, max_t=1):
        vectors_top = self.get_vectors_bot(t, max_t)
        vec_normal = self.get_normal()
        for n in range(len(vectors_top)):
            vectors_top[n] += vec_normal*self.height

        return vectors_top

    def move(self):
        if self.dir == 0:
            return False
        
        vec_dir = None
        if self.dir == LEFT:
            vec_dir = self.get_vec_left()
        else:
            vec_dir = self.get_vec_right()

        dest = self.center + (vec_dir * self.speed * framework.frame_time)

        if self.set_pos(dest) == False:
            self.stop()
            return False
        
        return True

    def start_move(self, dir):
        self.dir += dir

    def stop(self):
        self.dir = 0

    def update_ground(self):
        if self.is_floating():
            self.attach_ground(True)

    # _BUG_ : pass through a thin wall
    def get_vec_highest(self, ignore_height=False):
        vectors_bot = self.get_vectors_bot()
        bot_cells = gmap.get_cells(vectors_bot)

        vec_highest = Vector2.zero()
        vec_befroe : Vector2 = None

        # Set max length
        max_length = 0
        idx_highest = 0
        if ignore_height or not self.is_created:
            max_length = float('inf')
        else:
            max_length = self.get_rect().height / 2

        # Find
        for idx, cell in enumerate(bot_cells):
            result = gmap.get_highest_ground_cell(cell[0], cell[1], max_length, True)
            if result is False:
                continue
            
            col, row = result
            _, height = gmap.get_pos_from_cell(col, row)
            if height > vec_highest.y:
                vec_highest.x = vectors_bot[idx].x
                vec_highest.y = height
                vec_befroe = vectors_bot[idx]
                idx_highest = idx

        return vec_befroe, vec_highest, idx_highest

    def attach_ground(self, ignore_height=False):
        vec_befroe, vec_pivot, idx_pivot = self.get_vec_highest(ignore_height)
        if vec_befroe is None:
            return False, False

        dy = vec_pivot.y - vec_befroe.y
        self.offset(0, dy)

        return vec_pivot, idx_pivot

    def rotate_ground(self, ignore_height=False, ignore_size=False):
        vec_pivot, idx_pivot = self.attach_ground(ignore_height)
        if vec_pivot is False:
            if self.is_created: # delete : fall
                self.invalidate()
                delete_object(self)
            return False
        vectors_bot = self.get_vectors_bot()

        # set rotation direction
        dir_check = LEFT
        if vec_pivot.x < self.bot_center.x:
            dir_check = RIGHT
            
        axis = Vector2()
        if dir_check == LEFT:
            axis = Vector2.left()
        else:
            axis = Vector2.right()

        max_y = self.bot_center.y + self.width//2
        min_y = self.bot_center.y - self.width//2
        # get minimum theta
        min_theta = float("inf")
        for vector in vectors_bot:
            if dir_check == RIGHT:
                if vector.x < self.bot_center.x:
                    continue
            else:
                if vector.x > self.bot_center.x:
                    continue

            cell = gmap.get_cell(vector)
            if gmap.out_of_range_cell(cell[0], cell[1]):
                continue

            ground_cell = gmap.get_highest_ground_cell(*cell, is_cell=True)
            if ground_cell is False:
                continue
                
            vec_ground = Vector2(*gmap.get_pos_from_cell(*ground_cell))
            if ignore_size == False and (vec_ground.y > max_y or vec_ground.y < min_y):
                continue
            
            theta = vec_ground.get_theta_axis(axis, vec_pivot)
            if dir_check == RIGHT:
                theta *= -1

            if math.fabs(theta) < math.fabs(min_theta):
                min_theta = theta
        
        # didn't find highest ground point for bottom vectors
        if min_theta == float("inf"):
            min_theta = self.theta
        elif math.fabs(math.degrees(min_theta)) > 75 and ignore_height == False:
            return False

        # rotation and set position to ground
        self.set_theta(min_theta)
        self.attach_ground()
        vectors_bot = self.get_vectors_bot()
        if idx_pivot >= len(vectors_bot):
            idx_pivot = len(vectors_bot) - 1

        vector_correction = (vec_pivot - vectors_bot[idx_pivot])

        prev_center = self.center
        self.set_center((self.center[0] + vector_correction[0], self.center[1] + vector_correction[1]))
        if ignore_height == False and self.is_on_edge():
            self.set_center(prev_center)

        if self.is_floating():
            self.attach_ground()

        if self.is_on_edge():
            return False

        return True

    def is_on_edge(self):
        if self.dir == 0:
            return False

        vectors_bot = self.get_vectors_bot()
        max_length = self.width / 2
        for vector in vectors_bot:
            if self.dir == RIGHT:
                if vector.x < self.bot_center.x:
                    continue
            else:
                if vector.x > self.bot_center.x:
                    continue
            
            cell = gmap.get_cell(vector)
            ground_cell = gmap.get_highest_ground_cell(*cell, is_cell=True)
            if ground_cell is not False:
                ground_point = Vector2(*gmap.get_pos_from_cell(*ground_cell))
                length = (self.bot_center - ground_point).get_norm()
                if length <= max_length:
                    return False
        return True

    def is_floating(self):
        vectors_bot = self.get_vectors_bot()
        for vector in vectors_bot:
            cell = gmap.get_cell(vector)
            if gmap.get_block_cell(cell):
                return False
            
        return True



class FlyObject(GameObject):
    def __init__(self, image : Image, center=(0, 0), width=0, height=0, theta=0, dir=0, image_flip=''):
        self.image = image
        self.image_flip = image_flip
        super().__init__(center, width, height, theta, dir)

    def move(self):
        self.center.x += (self.dir * self.speed * framework.frame_time)
        self.update_object()
        
        return True

    def draw(self):
        self.draw_image(self.image, flip=self.image_flip)



_gameObjects : list[GameObject] = []
_groundObjects : list[GroundObject] = []
_flyObjects : list[FlyObject] = []

_list_map : dict = {
    GroundObject : _groundObjects,
    FlyObject : _flyObjects,
}


def enter():
    pass
    
def exit():
    global _gameObjects, _groundObjects, _flyObjects
    for object in _gameObjects:
        delete_object(object)
    _gameObjects.clear()
    _groundObjects.clear()
    _flyObjects.clear()
    
def update():
    for object in _gameObjects:
        object.update()

def draw():
    for object in reversed(_gameObjects):
        if object.is_draw:
            object.draw()

def add_object(object : GameObject):
    _gameObjects.append(object)

    parent = object.__class__.__base__
    while parent != GameObject:
        if parent in _list_map:
            object_list = _list_map[parent]
            object_list.append(object)
        parent = parent.__base__

def delete_object(object : GameObject):
    if object not in _gameObjects:
        assert(0)
        
    _gameObjects.remove(object)

    parent = object.__class__.__base__
    while parent != GameObject:
        if parent in _list_map:
            object_list = _list_map[parent]
            object_list.remove(object)
        parent = parent.__base__

    object.release()
    #del object

def get_gameObjects():
    return _gameObjects

def check_ground(position : Vector2, radius):
    for object in _groundObjects:
        if object.is_in_radius(position, radius):
            object.invalidate()
            object.rotate_ground(True, True)
            object.is_rect_invalid = True