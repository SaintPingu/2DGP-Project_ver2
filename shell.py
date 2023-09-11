if __name__ == "__main__":
    quit()

from tools import *
import object
import gmap
import sprite
import tank
import sound
import framework

DEFAULT_SHELL = "AP"

SHELLS : dict
EXPLOSIONS : dict

SOUND_CHANNEL_HOMING = 1

def enter():
    global SHELLS, EXPLOSIONS, fired_shells
    img_shell_ap = load_image_path('shell_ap.png')
    img_shell_hp = load_image_path('shell_hp.png')
    img_shell_mul = load_image_path('shell_multiple.png')
    img_shell_nuclear = load_image_path('shell_nuclear.png')
    img_shell_teleport = load_image_path('shell_teleport.png')
    img_shell_homing = load_image_path('shell_homing.png')
    SHELLS = { "AP" : img_shell_ap, "HP" : img_shell_hp, "MUL" : img_shell_mul, "NUCLEAR" : img_shell_nuclear, "TP" : img_shell_teleport, "HOMING" : img_shell_homing}
    EXPLOSIONS = {
        "AP" : "Explosion",
        "HP" : "Explosion",
        "MUL" : "Explosion",
        "NUCLEAR" : "Explosion_Nuclear",
        "HOMING" : "Explosion",
    }

    fired_shells = []

def exit():
    global SHELLS, EXPLOSIONS, fired_shells
    for image in SHELLS.values():
        del image
    del SHELLS
    
    EXPLOSIONS.clear()
    del EXPLOSIONS
    
    for shell in fired_shells:
        delete_shell(shell)

    fired_shells.clear()
    del fired_shells


class Shell(object.GameObject):
    name_table = {
        "AP" : "Armour-Piercing",
        "HP" : "High-Explosive",
        "MUL" : "Multiple",
        "NUCLEAR" : "Nuclear",
        "TP" : "Teleport",
        "HOMING" : "Homing",
    }
    MIN_POWER = 0.2
    SIMULATION_t = 0.15
    def __init__(self, shell_name : str, position, theta, power = 1, is_simulation=False, delay = 0):
        self.img_shell : Image = get_shell_image(shell_name)

        super().__init__(position, self.img_shell.w, self.img_shell.h, theta)

        self.shell_name = shell_name
        self.origin = Vector2(*position)
        self.start_theta = theta

        self.vector = Vector2.right().get_rotated(theta)
        self.speed, self.shell_damage, self.explosion_damage, self.explosion_radius = get_attributes(shell_name)
        if self.speed <= 0:
            raise Exception

        if power < Shell.MIN_POWER:
            power = Shell.MIN_POWER
        elif power > 1:
            power = 1
        self.speed *= power

        self.is_destroyed = False 
        self.DETECTION_RADIUS = 2
        self.prev_head : Vector2() = None

        self.is_simulation = is_simulation
        if is_simulation:
            self.shell_damage = 0
            self.explosion_damage = 0

        self.t = 0
        self.delay = delay
        self.sub = False
        self.is_teleport = False

    def draw(self):
        if self.delay > 0:
            return

        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
    
    def move(self, is_affected_wind=True):
        from state_battle import get_gravity
        dest = Vector2()
        
        # Use projectile moition formula
        if not self.is_simulation:
            self.t += (self.speed/20 * framework.frame_time)
        else:
            self.t += Shell.SIMULATION_t # faster search
            
        dest.x = self.origin.x + (self.speed * self.t * math.cos(self.start_theta))
        dest.y = self.origin.y + (self.speed * self.t * math.sin(self.start_theta) - (0.5 * get_gravity() * self.t**2))

        # not applied air resistance
        # and this is not drag
        if is_affected_wind:
            dest.x += gmap.env.get_wind() * self.t

        self.vector = self.vector.get_rotated_dest(self.center, dest)
        self.set_center(dest)
        

    def update(self):
        if self.delay > 0:
            self.delay -= framework.frame_time
            if self.delay <= 0 and not self.sub:
                sprite.add_animation("Shot", self.origin, self.start_theta)
                play_fire_sound(self.shell_name)
            return

        self.invalidate()
        rect = self.get_square()

        # out of range
        a = rect.right < rect.width // 2
        b = rect.left > SCREEN_WIDTH - rect.width // 2
        c = rect.bottom <= MIN_HEIGHT
        d = rect.top <= MIN_HEIGHT
        if a or b or c or d:
            if a:
                self.set_center((SCREEN_WIDTH - rect.width // 2, self.center.y))
                self.origin.x = SCREEN_WIDTH + self.origin.x
            elif b:
                self.set_center((rect.width // 2, self.center.y))
                self.origin.x = self.origin.x - SCREEN_WIDTH
            else:
                self.explosion(self.get_head())
                return False
            rect = self.get_square()
        
        head = self.get_head()
        if self.prev_head is None:
            self.prev_head = head

        collision_vectors = gmap.get_vectors(head, self.prev_head)

        target_tank = self.check_tanks(head, collision_vectors)
        if target_tank is not False:
            return target_tank
        elif self.check_grounds(head) == True:
            return False

        self.is_rect_invalid = True

        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y <= 0:
            self.theta *= -1
            
        self.move()
        self.prev_head = head

        return True
    
    # Check collision by tanks
    def check_tanks(self, head, collision_vectors):
        head = self.get_head()
        target_tank = tank.check_hit(head, collision_vectors, self.DETECTION_RADIUS, self.shell_damage)
        if target_tank is False:
            return False

        explosion_pos = head + (target_tank.center - head)*0.5
        self.explosion(explosion_pos)
        return target_tank

    # Check collision by grounds
    def check_grounds(self, head):
        rect_detection = Rect(head, self.DETECTION_RADIUS*2, self.DETECTION_RADIUS*2)
        detected_cells = gmap.get_detected_cells(rect_detection)
        if is_debug_mode():
            gmap.draw_debug_rect(rect_detection)

        for detected_cell in detected_cells:
            if not gmap.out_of_range_cell(*detected_cell) and gmap.get_block_cell(detected_cell):
                self.explosion(head)
                return True
        return False

    def invalidate(self, is_grid=False):
        if self.is_simulation:
            return

        if is_grid:
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
        else:
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True, grid_size=0)

    def explosion(self, head : Vector2):
        if self.is_simulation:
            return

        if self.is_teleport:
            tank.teleport(head)
        else:
            gmap.draw_block(self.explosion_radius, head, False)
            tank.check_explosion(head, self.explosion_radius, self.explosion_damage)
            object.check_ground(head, self.explosion_radius + 10)
            sprite.add_animation(EXPLOSIONS[self.shell_name], head, scale=self.explosion_radius/10)
            self.invalidate()
            sound.play_sound('explosion', 100)

        delete_shell(self)

    def get_head(self) -> Vector2:
        return self.center + (self.vector.normalized() * self.img_shell.w/gmap.CELL_SIZE)

    def set_sub(self):
        self.sub = True

class Shell_Homing(Shell):
    SPEED_LOCK_ON = 2
    MAX_DISTANCE = 500
    def __init__(self, shell_name: str, position, theta, target_pos : Vector2, power=1, is_simulation=False, delay=0, id=0):
        assert(target_pos is not None)

        super().__init__(shell_name, position, theta, power, is_simulation, delay)
        self.target_pos = target_pos
        self.guide_t = 0
        self.is_locked = False
        self.gui_lock = None
        self.id = id
    
    def release(self):
        super().release()
        sound.stop_channel(SOUND_CHANNEL_HOMING + self.id)
        if self.gui_lock != None:
            import gui
            gui.del_gui(self.gui_lock)
            self.gui_lock = None
    
    def move(self):
        if not self.is_locked:
            if self.is_blocked():   # blocked by block
                super().move()
                return
            self.target_lock()
        
        self.vec_dest = self.vector.get_rotated_dest(self.center, self.target_pos)
        dir = get_sign(Vector2.cross(self.vector, self.vec_dest))

        self.vector = self.vector.get_rotated(framework.frame_time * dir * Shell_Homing.SPEED_LOCK_ON)
        dest = self.center + (self.vector * self.speed * framework.frame_time)
        self.set_center(dest)
    
    # search blocks between self.center and target_pos
    def is_blocked(self):
        if (self.center - self.target_pos).get_norm() >= Shell_Homing.MAX_DISTANCE:
            return True

        toTargetVectors = gmap.get_vectors(self.center, self.target_pos)

        for vector in toTargetVectors:
            cell = gmap.get_cell(vector)

            if gmap.get_block(*cell) == True:   
                return True

        return False

    def target_lock(self):
        import gui
        sound.play_sound('lock_on', 128, channel=SOUND_CHANNEL_HOMING + self.id)
        self.is_locked = True   # can hit
        self.speed = get_attributes("HOMING")[0] * 4
        lock_image = load_image_path('target_lock.png')
        self.gui_lock = gui.GUI(lock_image, self.target_pos, is_fixed=True)
        gui.add_gui(self.gui_lock, 0)
    

fired_shells : list[Shell]

def add_shell(shell_name, head_position, theta, power = 1, item = None, target_pos=None):
    delay = 0
    count_shot = 1
    if item == "double":
        count_shot = 2

    for i in range(count_shot):

        if shell_name == "HOMING":
            shell = Shell_Homing(shell_name, head_position, theta, target_pos, power, delay=delay, id=i)
        else:
            shell = Shell(shell_name, head_position, theta, power, delay=delay)

        shell_head = shell.get_head()
        position = head_position + (head_position - shell_head)
        shell.set_pos(position)
        fired_shells.append(shell)
        object.add_object(shell)

        if shell_name == "MUL":
            for n in range(3):
                t = 0.05 * (n+1)
                shell_1 = Shell(shell_name, position, theta + t, power, delay=delay)
                shell_2 = Shell(shell_name, position, theta - t, power, delay=delay)
                shell_1.set_sub()
                shell_2.set_sub()
                fired_shells.append(shell_1)
                fired_shells.append(shell_2)
                object.add_object(shell_1)
                object.add_object(shell_2)

        delay += 2

    
    if item == "extension":
        for shell in fired_shells:
            shell.explosion_radius *= 2
    elif item == "TP":
        shell.is_teleport = True
        shell.shell_damage = 0
        shell.img_shell = get_shell_image("TP")
        shell.speed = get_attributes("TP")[0] * power
            


def delete_shell(shell : Shell):
    if shell.is_simulation is True:
        return

    if shell in fired_shells:    
        fired_shells.remove(shell)
        object.delete_object(shell)

def get_attributes(shell_name : str) -> tuple[float, float]:
    speed = 0
    shell_damage = 0
    explosion_damage = 0
    explosion_radius = 0

    if shell_name == "HP":
        speed = 350
        shell_damage = 20
        explosion_damage = 20 
        explosion_radius = 15
    elif shell_name == "AP":
        speed = 400
        shell_damage = 30
        explosion_damage = 5
        explosion_radius = 8
    elif shell_name == "MUL":
        speed = 300
        shell_damage = 5
        explosion_damage = 10
        explosion_radius = 4
    elif shell_name == "NUCLEAR":
        speed = 375
        shell_damage = 5
        explosion_damage = 30
        explosion_radius = 22
    elif shell_name == "TP":
        speed = 300
    elif shell_name == "HOMING":
        speed = 400
        shell_damage = 15
        explosion_damage = 2
        explosion_radius = 5
    else:
        assert(0)

    speed_pps = get_pps(speed)
    shell_damage *= 2
    explosion_damage *= 2
    return speed_pps, shell_damage, explosion_damage, explosion_radius

def get_shell_image(shell_name):
    assert shell_name in SHELLS.keys()

    return SHELLS[shell_name]

def play_fire_sound(shell_name):
    assert shell_name in SHELLS.keys()

    if shell_name == "HOMING":
        sound.play_sound('tank_fire_homing', 64)
    else:
        sound.play_sound('tank_fire_general', 64)