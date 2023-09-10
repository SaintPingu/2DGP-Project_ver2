if __name__ == "__main__":
    quit()

from pico2d import *
import math
import random
import time

_is_debug_mode = False

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1000
MIN_HEIGHT = 108
MAX_HEIGHT = 700

LEFT = -1
RIGHT = 1

END_OF_LINE = 'END\n'

PIXEL_PER_METER = 1

NO_WIND_MAPS = [4,]

class Vector2:
    def __init__(self, x=0, y=0):
        self.x : float = x
        self.y : float = y

    def __call__(self):
        return self.x, self.y
    
    def __getitem__(self):
        return (self.x, self.y)
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, other):
        return Vector2(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)
    
    def __truediv__(self, other : float):
        return Vector2(self.x / other, self.y / other)
    
    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def left():
        return Vector2(-1, 0)
    def right():
        return Vector2(1, 0)
    def up():
        return Vector2(0, 1)
    def down():
        return Vector2(0, -1)
    def zero():
        return Vector2(0, 0)

    def normalize(self):
        norm = self.get_norm()
        self /= norm

    def normalized(self):
        norm = self.get_norm()
        self /= norm
        return self

    def get_norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y)
    
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def get_theta(self, other):
        dot = self.dot(other)
        return math.acos(dot / (self.get_norm() * other.get_norm()))

    def get_theta_axis(self, axis, origin):
        self -= origin
        dot = self.dot(axis)
        return math.acos(dot / (self.get_norm() * axis.get_norm()))

    def get_dest(self, vector_dir, speed : float):
        return self + (vector_dir * speed)

    # rotate self(unit direction vector) to vec_dest
    def get_rotated_dest(self, vec_src, vec_dest, t=1): # t=0~1
        vec_to_target = (vec_dest - vec_src).normalized()
        a = math.atan2(self.x, self.y)
        b = math.atan2(vec_to_target.x, vec_to_target.y)
        theta = (a - b) * t

        return self.get_rotated(theta * t)
    def get_rotated(self, theta):
        result = Vector2()
        result.x = (self.x * math.cos(theta)) - (self.y * math.sin(theta))
        result.y = (self.x * math.sin(theta)) + (self.y * math.cos(theta))

        return result

    def get_rotated_pivot(self, pivot, theta):
        if type(pivot) != Vector2:
            pivot = Vector2(*pivot)

        result = self
        result -= pivot
        
        return pivot + result.get_rotated(theta)
    
    def lerp(self, dst, t):
        transform = Vector2()
        transform.x = (self.x * (1 - t)) + (dst.x * t)
        transform.y = (self.y * (1 - t)) + (dst.y * t)
        return transform
        

class Rect:
    def __init__(self, center=(0,0), width=0, height=0):
        self.center : tuple = center
        self.origin : tuple = (0,0)
        self.width : float = width
        self.height : float = height

        self.left : float = 0
        self.right : float = 0
        self.top : float = 0
        self.bottom : float = 0

        self.set_pos(center)

    def __getitem__(self):
        return (self.center, self.width, self.height)
    
    def set_origin(self, origin, width, height):
        self.width = width
        self.height = height
        self.origin = origin
        self.center = [origin[0] + (self.width//2), origin[1] + (self.height//2)]
        self.set_pos(self.center)

    def set_pos(self, center):
        self.center = center
        self.left = center[0] - (self.width//2)
        self.right = center[0] + (self.width//2)
        self.top = center[1] + (self.height//2)
        self.bottom = center[1] - (self.height//2)
        self.origin = (self.left, self.bottom)
    
    def get_rect_int(self):
        result = Rect()
        result.center = to_int_pos(self.center)
        result.width = math.ceil(self.width)
        result.height = math.ceil(self.height)
        result.update()
        return result

    def get_fCenter(self):
        return [self.origin[0] + (self.width/2), self.origin[1] + (self.height/2)]

    def update(self):
        self.set_pos(self.center)
        
    def collide_point(self, x, y):
        if x >= self.left and x <= self.right and y >= self.bottom and y <= self.top:
            return True
        return False
    
    def collide_rect(self, other):
        if self.left > other.right or self.right < other.left or self.bottom > other.top or self.top < other.bottom:
            return False
        
        return True
    
    def move(self, x, y):
        self.center = (self.center[0] + x, self.center[1] + y)
        self.update()

    def get_copy(self):
        result = Rect()
        result.center = self.center
        result.width = self.width
        result.height = self.height
        result.update()
        return result

# Invalidation Rectangle
class InvRect(Rect):
    def __init__(self, center=(0,0), width=0, height=0, is_filled=False, is_empty=False):
        super().__init__(center, width, height)
        self.is_filled = is_filled
        self.is_empty = is_empty
        self.is_grid = True


##### TOOLS #####
def convert_pico2d(x, y):
    return x, SCREEN_HEIGHT - 1 - y
    
def load_image_path(image : str):
    name = 'images/' + image
    result = load_image(name)
    if _is_debug_mode:
        print('load image : ' + name)

    return result

def load_font_path(font : str, size = 20):
    name = 'fonts/' + font + '.ttf'
    result = load_font(name, size)
    if _is_debug_mode:
        print('load font : ' + name)

    return result

def load_music_path(music : str):
    name = 'sounds/' + music + '.mp3'
    result = load_music(name)
    if _is_debug_mode:
        print('load music : ' + name)

    return result

def load_wav_path(wav : str):
    name = 'sounds/' + wav + '.wav'
    result = load_wav(name)
    if _is_debug_mode:
        print('load wav : ' + name)
    
    return result

def out_of_range(x, y, max_x, max_y):
    return ((x < 0) or (x >= max_x) or (y < 0) or (y >= max_y))

def get_length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def to_int_pos(position):
    return (int(position[0]), int(position[1]))

def get_sign(num):
    return num / math.fabs(num)
def is_debug_mode():
    return _is_debug_mode
def set_debug_mode(is_debug_mode):
    global _is_debug_mode
    _is_debug_mode = is_debug_mode
def toggle_debug_mode():
    global _is_debug_mode
    _is_debug_mode = not _is_debug_mode

def point_in_rect(point, rect : Rect):
    if (point[0] > rect.left and point[0] < rect.right) and (point[1] < rect.top and point[1] > rect.bottom):
        return True
    
    return False

def get_pps(kmph):
    mpm = (kmph * 1000.0 / 60.0)
    mps = (mpm / 60.0)
    return (mps * PIXEL_PER_METER)