if __name__ == "__main__":
    quit()

from tools import *

class Inventory:
    NUM_OF_SLOT = 9
    def __init__(self, image : Image, position : tuple, slot_position : tuple):
        from gui import GUI
        self.gui = GUI(image, position, is_fixed=True)
        self.rect = self.gui.get_rect()
        self.slot_items = []

        self.slots : list[Rect] = []
        slot_width = 34
        slot_height = 34
        slot_interval = slot_width + 2
        for i in range(Inventory.NUM_OF_SLOT):
            rect = Rect((slot_position[0] + (i * slot_interval), slot_position[1]), slot_width, slot_height)
            self.slots.append(rect)
    
    def exit(self):
        del self.gui
        del self.rect

        for rect in self.slots:
            del rect
        del self.slots

    def select(self, target_tank, index):
        if index < len(self.slot_items):
            return True
        return False

    def draw(self):
        self.gui.draw()

    def add_item(self, item):
        self.slot_items.append(item)

class Inven_Weapon(Inventory):
    weapons = ( "AP", "HP", "MUL", "NUCLEAR", "HOMING" )
    background : Image
    def __init__(self):
        position = (555, 140)
        super().__init__(Inven_Weapon.background, position, (555 - 145, 140))
    
        for weapon in Inven_Weapon.weapons:
            self.slot_items.append(weapon)
        
    def draw(self):
        from shell import get_shell_image
        super().draw()
        for idx, item in enumerate(self.slot_items):
            image : Image = get_shell_image(item)
            rect : Rect = self.slots[idx]
            image.composite_draw(math.radians(90), '', *rect.center)

    def select(self, target_tank, index):
        if super().select(target_tank, index) == False:
            return

        if target_tank.inven_item.get_item() == "TP":
            target_tank.inven_item.deselect()

        from gui import gui_weapon
        shell_name = self.slot_items[index]
        target_tank.crnt_shell = shell_name

        gui_weapon.set_image(shell_name)

class Inven_Item(Inventory):
    background : Image = None
    image_double : Image = None
    image_extension : Image = None
    image_teleport : Image = None
    image_heal : Image = None
    item_table : dict = {}
    items : list

    def __init__(self):
        position = (345, 140)
        self.item_used = False
        self.crnt_item = None
        super().__init__(Inven_Item.background, position, (345 - 145, 140))
    
    def draw(self):
        super().draw()
        for idx, item in enumerate(self.slot_items):
            image : Image = Inven_Item.item_table[item]
            rect : Rect = self.slots[idx]
            image.draw(*rect.center)

    def select(self, target_tank, index):
        if super().select(target_tank, index) == False:
            return
        elif self.item_used == True:
            return
        
        item = self.slot_items.pop(index)
        self.use_item(target_tank, item)

    def use_item(self, tank, item_name):
        if self.crnt_item != None:
            self.deselect()

        self.crnt_item = item_name

        import gui
        if self.crnt_item == "heal":
            if tank.hp >= tank.max_hp:
                self.add_item("heal")
                self.crnt_item = None
                gui.gui_weapon.set_item(None)
                return
            self.item_used = True
            tank.hp += 15
            tank.hp = clamp(0, tank.hp, tank.max_hp)
            
            gui.gui_weapon.set_item(None)
            gui.gui_weapon.set_image(tank.crnt_shell)
        elif self.crnt_item == "TP":
            gui.gui_weapon.set_item(None)
            gui.gui_weapon.set_image(item_name)
        else:
            gui.gui_weapon.set_item(self.item_table[item_name])
        
    def get_item(self):
        return self.crnt_item
    
    def deselect(self):
        self.add_item(self.crnt_item)
        self.item_used = False
        self.crnt_item = None
    
    def reset(self):
        self.crnt_item = None
        self.item_used = False
    
    def select_random_item(self, tank):
        if len(self.slot_items) <= 0:
            return

        index = random.randint(0, len(self.slot_items) - 1)
        self.select(tank, index)


_crnt_inventory : Inventory = None
def set_inventory(inventory : Inventory):
    hide_inventory()

    global _crnt_inventory
    if inventory != _crnt_inventory:
        _crnt_inventory = inventory

def hide_inventory():
    global _crnt_inventory
    if _crnt_inventory != None:
        _crnt_inventory.gui.invalidate()
        _crnt_inventory = None

def enter():
    Inven_Item.background = load_image_path('inventory_item.png')
    Inven_Item.image_double = load_image_path('item_double.png')
    Inven_Item.image_extension = load_image_path('item_extension.png')
    Inven_Item.image_teleport = load_image_path('shell_teleport.png')
    Inven_Item.image_heal = load_image_path('item_heal.png')

    item_table = {
        'double' : Inven_Item.image_double,
        'extension' : Inven_Item.image_extension,
        'TP' : Inven_Item.image_teleport,
        'heal' : Inven_Item.image_heal,
    }
    Inven_Item.item_table.update(item_table)
    Inven_Item.items = [ name for name in Inven_Item.item_table.keys() ]

    Inven_Weapon.background = load_image_path('inventory_weapon.png')

def exit():
    del Inven_Item.background
    del Inven_Item.image_double
    del Inven_Item.image_extension
    del Inven_Item.image_teleport
    del Inven_Item.image_heal

    del Inven_Weapon.background

def draw():
    if _crnt_inventory != None:
        _crnt_inventory.draw()


def check_select(crnt_tnak, point):
    if _crnt_inventory == None:
        return False
        
    if point_in_rect(point, _crnt_inventory.rect):
        for idx, rect in enumerate(_crnt_inventory.slots):
            if point_in_rect(point, rect):
                from sound import play_sound
                play_sound('click')
                _crnt_inventory.select(crnt_tnak, idx)
                hide_inventory()
                return True

    return False

def pause():
    pass
def resume():
    pass