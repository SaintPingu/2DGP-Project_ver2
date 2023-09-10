if __name__ == "__main__":
    quit()

from tools import *
import object
import environment as env


CELL_SIZE = 2   # recommend an even number (min : 2)

X_CELL_COUNT = SCREEN_WIDTH // CELL_SIZE
Y_CELL_COUNT = (SCREEN_HEIGHT-MIN_HEIGHT) // CELL_SIZE
Y_CELL_MIN = MIN_HEIGHT//CELL_SIZE

_crnt_map : list[list[bool]]


_img_background : Image
_img_ground : Image

DEFAULT_DRAW_RADIUS = 3
_radius_draw = DEFAULT_DRAW_RADIUS
is_draw_mode = False
_is_create_block = False
_is_delete_block = False
_is_print_mouse_pos = False

_rect_inv_list : list[InvRect]
_rect_debug_list : list[InvRect]

selected_tank = None

def enter():
    global _rect_inv_list, _rect_debug_list
    _rect_inv_list = []
    _rect_debug_list = []

def exit():
    global _img_background, _img_ground
    del _img_background
    del _img_ground

    global _rect_inv_list, _rect_debug_list
    for rect in _rect_inv_list:
        del rect
    for rect in _rect_debug_list:
        del rect
    _rect_inv_list.clear()
    _rect_debug_list.clear()
    del _rect_inv_list
    del _rect_debug_list
    _rect_inv_list = None
    _rect_debug_list = None

    global selected_tank
    selected_tank = None

    global _crnt_map
    _crnt_map.clear()
    del _crnt_map

def draw(is_draw_full=False):
    global _rect_inv_list

    if is_draw_full:
        _rect_inv_list.clear()
        _rect_inv_list.append(InvRect((SCREEN_WIDTH//2, SCREEN_HEIGHT//2), SCREEN_WIDTH, SCREEN_HEIGHT))

    # draw background
    for rect_inv in list(_rect_inv_list):
        if is_debug_mode():
            draw_debug_rect(rect_inv)

        if rect_inv.is_grid == False:
            block_set = get_block_set(rect_inv)
            if False not in block_set:
                rect_inv.is_filled = True
            elif True not in block_set:
                rect_inv.is_empty = True

        if rect_inv.is_filled:
            draw_ground(rect_inv)
            _rect_inv_list.remove(rect_inv)
            continue
        elif rect_inv.is_empty:
            _rect_inv_list.remove(rect_inv)

        draw_background(rect_inv)

    # draw grounds
    for rect_inv in _rect_inv_list:
        cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)

        for cell_y in range(cell_start_y, cell_end_y + 1):
            for cell_x in range(cell_start_x, cell_end_x + 1):
                if out_of_range_cell(cell_x, cell_y):
                    continue
                elif get_block(cell_x, cell_y) == False:
                    continue

                posX, posY = get_pos_from_cell(cell_x, cell_y)
                originX, originY = get_origin_from_cell(cell_x, cell_y)

                _img_ground.clip_draw(originX, originY, CELL_SIZE, CELL_SIZE, posX, posY)


    _rect_inv_list.clear()


def handle_draw_mode_events(events : list):
    import tank
    global is_draw_mode
    global _is_create_block, _is_delete_block, _is_print_mouse_pos
    global _radius_draw
    global selected_tank
    
    event : Event
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == None:
                continue
            elif SDLK_1 <= event.key <= SDLK_9:
                _radius_draw = event.key - SDLK_0
                if selected_tank:
                    if event.key == SDLK_1:
                        selected_tank.set_team("green")
                    elif event.key == SDLK_2:
                        selected_tank.set_team("blue")
                    elif event.key == SDLK_3:
                        selected_tank.set_team("red")
            elif event.key == SDLK_KP_MULTIPLY:
                _radius_draw *= 2
            elif event.key == SDLK_KP_DIVIDE:
                _radius_draw //= 2
            elif event.key == SDLK_F1:
                stop_draw_mode()
                return
            elif event.key == SDLK_F2:
                toggle_debug_mode()
                continue
            elif event.key == SDLK_F3:
                env.toggle_show_clouds()
            elif event.key == SDLK_F5:
                save_mapfile()
            elif event.key == SDLK_F6:
                draw(True)
            elif event.key == SDLK_F7:
                env.randomize_wind()
            elif event.key == SDLK_F9:
                if selected_tank == None:
                    selected_tank = tank.new_tank()
                else:
                    selected_tank.invalidate()
                    object.delete_object(selected_tank)
                    selected_tank = None
            elif event.key == SDLK_F10:
                _is_print_mouse_pos = not _is_print_mouse_pos
            continue

        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                if selected_tank:
                    selected_tank.create()
                    tank.select_tank(selected_tank)
                    selected_tank = None
                    continue
                _is_create_block = True
            elif event.button == SDL_BUTTON_RIGHT:
                _is_delete_block = True

        elif event.type == SDL_MOUSEBUTTONUP:
            _is_create_block = False
            _is_delete_block = False
            continue

        mouse_pos = ()
        if event.x != None:
            mouse_pos = convert_pico2d(event.x, event.y)
        else:
            continue
        
        if selected_tank and selected_tank.is_created == False:
            selected_tank.invalidate()
            selected_tank.set_pos(mouse_pos)
        elif _is_create_block:
            create_block(_radius_draw, mouse_pos)
        elif _is_delete_block:
            delete_block(_radius_draw, mouse_pos)
        
        if _is_print_mouse_pos:
            print(mouse_pos)
    
def start_draw_mode():
    global is_draw_mode
    is_draw_mode = True

def stop_draw_mode():
    global is_draw_mode, _radius_draw
    _radius_draw = DEFAULT_DRAW_RADIUS
    is_draw_mode = False

def draw_ground(rect : Rect):
    _img_ground.clip_draw(int(rect.origin[0]), int(rect.origin[1]), int(rect.width), int(rect.height), *rect.get_fCenter())
def draw_background(rect : Rect, is_resized=True):
    if is_resized is False:
        rect = Rect.get_rect_int(rect)
        resize_rect_inv(rect)
    _img_background.clip_draw(int(rect.origin[0]), int(rect.origin[1]), int(rect.width), int(rect.height), *rect.get_fCenter())

def get_block_set(rect_inv : Rect):
    cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)
    sliced_map = get_sliced_map(cell_start_x, cell_start_y, cell_end_x, cell_end_y)

    block_set = set()
    for row in sliced_map:
        block_set |= (set(row))
    return block_set



##### BLOCK #####
def create_block(radius, mouse_pos):
    draw_block(radius, mouse_pos, True)

def delete_block(radius, mouse_pos):
    draw_block(radius, mouse_pos, False)

def draw_block(radius, position, is_block):
    col, row = get_cell(position)
    x = -radius

    COLL_VAL = 0.5
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            cell_x = col+x
            cell_y = row+y
            if out_of_range_cell(cell_x, cell_y):
                continue
            elif cell_y >= MAX_HEIGHT//CELL_SIZE:
                continue
            elif get_block(cell_x, cell_y) == is_block:
                continue
            cell_pos = get_pos_from_cell(cell_x, cell_y)
            distance = (Vector2(*position) - Vector2(*cell_pos)).get_norm()
            if distance <= radius * CELL_SIZE + COLL_VAL:
                set_block(cell_x, cell_y, is_block)

    add_invalidate(position, radius*2 * CELL_SIZE, radius*2 * CELL_SIZE)




##### Invalidate #####
def resize_rect_inv(rect : Rect):
    if rect.left < 0:
        rect.set_origin((0, rect.bottom), rect.right + 1, rect.height)
    elif rect.right > SCREEN_WIDTH:
        rect.set_origin((rect.left, rect.bottom), SCREEN_WIDTH - rect.left + 1, rect.height)

    if rect.bottom <= MIN_HEIGHT:
        rect.set_origin((rect.left, MIN_HEIGHT), rect.width, rect.top - MIN_HEIGHT + 1)
    elif rect.top > SCREEN_HEIGHT:
        rect.set_origin((rect.left, rect.bottom), rect.width, SCREEN_HEIGHT - rect.bottom + 1)

# merge rectangles
def merge_rects(rect_left : InvRect, rect_right : InvRect):
    width = rect_right.right - rect_left.left
    height = rect_right.top - rect_left.bottom
    center = (rect_left.left + width//2, rect_left.bottom + height//2)
    return InvRect(center, width, height, rect_left.is_filled, rect_left.is_empty)

_DEFAULT_DIVIDE_GRID_SIZE = CELL_SIZE * 7
_MIN_DIVIDE_GRID_SIZE = CELL_SIZE * 4
def set_invalidate_rect(center, width=0, height=0, scale=1, square=False, grid_size=_DEFAULT_DIVIDE_GRID_SIZE):
    CORR_VAL = 4

    width *= scale
    height *= scale
    width += CORR_VAL
    height += CORR_VAL

    if square:
        if width > height:
            height = width
        else:
            width = height
    
    add_invalidate(center, width, height, grid_size)

def add_invalidate(center, width, height, grid_size=_DEFAULT_DIVIDE_GRID_SIZE):
    global _rect_inv_list

    rect_inv = Rect.get_rect_int(Rect(center, width, height))
    rect_inv = InvRect(*rect_inv.__getitem__())

    resize_rect_inv(rect_inv)

    if grid_size == 0 or (rect_inv.width <= grid_size and rect_inv.height <= grid_size):
        rect_inv.is_grid = False
        _rect_inv_list.append(rect_inv)
        return

    # Divide rectangles by grid
    max_row = rect_inv.height//grid_size
    max_col = rect_inv.width//grid_size

    is_before_line_filled = False
    is_before_line_empty = False
    line_before : InvRect = None

    for row in range(0, max_row + 1):
        empty_count = 0
        filled_count = 0
        rect_before : InvRect = None

        for col in range(0, max_col + 1):
            x = rect_inv.origin[0] + (col*grid_size) + grid_size//2
            y = rect_inv.origin[1] + (row*grid_size) + grid_size//2
            width, height = grid_size, grid_size

            # remaining top area
            if row == max_row:
                height = int(rect_inv.height%grid_size)
                y = rect_inv.top - height//2
            # remaining right area
            if col == max_col:
                width = int(rect_inv.width%grid_size)
                x = rect_inv.right - width//2

            center = (x, y)
            rect = InvRect(center, width, height)

            # merge rect in row #
            block_set = get_block_set(rect)
            # filled
            if False not in block_set:
                if empty_count > 0:
                    _rect_inv_list.append(rect_before)
                empty_count = 0

                if filled_count > 0:
                    rect = merge_rects(rect_before, rect)
                filled_count += 1
                rect.is_filled = True
            # empty
            elif True not in block_set:
                if filled_count > 0:
                    _rect_inv_list.append(rect_before)
                filled_count = 0
                
                if empty_count > 0:
                    rect = merge_rects(rect_before, rect)
                empty_count += 1
                rect.is_empty = True
            else:
                if grid_size > _MIN_DIVIDE_GRID_SIZE:   # partition
                    add_invalidate(*rect.__getitem__(), _MIN_DIVIDE_GRID_SIZE)
                else:
                    _rect_inv_list.append(rect)
                    
                if filled_count > 0 or empty_count > 0:
                    _rect_inv_list.append(rect_before)
                empty_count = 0
                filled_count = 0

            rect_before = rect
        
        # merge rect by row #
        if filled_count > 0 or empty_count > 0:
            # row is filled
            if filled_count > max_col:
                if is_before_line_empty:
                    _rect_inv_list.append(line_before)
                    line_before = None
                if line_before is None:
                    line_before = rect
                else:
                    line_before = merge_rects(line_before, rect)
                is_before_line_filled = True
                is_before_line_empty = False

            # row is empty
            elif empty_count > max_col:
                if is_before_line_filled:
                    _rect_inv_list.append(line_before)
                    line_before = None
                if line_before is None:
                    line_before = rect
                else:
                    line_before = merge_rects(line_before, rect)
                is_before_line_filled = False
                is_before_line_empty = True

            else:
                if line_before is not None:
                    _rect_inv_list.append(line_before)
                    line_before = None
                _rect_inv_list.append(rect_before)
                is_before_line_empty = False
                is_before_line_filled = False
        else:
            if line_before is not None:
                _rect_inv_list.append(line_before)
                line_before = None
            is_before_line_empty = False
            is_before_line_filled = False
            
    if line_before is not None:
        _rect_inv_list.append(line_before)







##### MAP #####
def out_of_range_cell(cell_x, cell_y):
    return ((cell_x < 0) or (cell_x >= X_CELL_COUNT) or (cell_y < 0) or (cell_y >= Y_CELL_COUNT))

def get_cell(position):
    return int(position[0]//CELL_SIZE), int((position[1]-MIN_HEIGHT)//CELL_SIZE)
def get_cells(positions):
    result = []
    for pos in positions:
        result.append(get_cell(pos))
    return result
    

def get_pos_from_cell(colIdx : int, rowIdx : int):
    return ((colIdx * CELL_SIZE) + CELL_SIZE//2), ((rowIdx * CELL_SIZE) + CELL_SIZE//2) + MIN_HEIGHT
def get_origin_from_cell(colIdx : int, rowIdx : int):
    return ((colIdx * CELL_SIZE) + CELL_SIZE//2) - CELL_SIZE//2, ((rowIdx * CELL_SIZE) + CELL_SIZE//2) - CELL_SIZE//2 + MIN_HEIGHT

def get_block(cell):
    if out_of_range_cell((cell[0], cell[1])):
        return False
    return _crnt_map[cell[1]][cell[0]]

def get_detected_cells(rect : Rect):
    global _crnt_map
    result = []
    cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect)
    for cell_y in range(cell_start_y, cell_end_y + 1):
        for cell_x in range(cell_start_x, cell_end_x + 1):
            if out_of_range_cell(cell_x, cell_y):
                continue
            block = _crnt_map[cell_y][cell_x]
            if block:
                result.append((cell_x, cell_y))
    
    return result
                
def get_start_end_cells(rect : Rect):
    cell_start_x, cell_start_y = get_cell(rect.origin)
    cell_end_x, cell_end_y = get_cell( (rect.origin[0] + rect.width, rect.origin[1] + rect.height) )
    return cell_start_x, cell_start_y, cell_end_x, cell_end_y

def get_block(col : int, row : int):
    if out_of_range_cell(col, row):
        return False
    return _crnt_map[row][col]
def get_block_cell(cell : tuple):
    return get_block(cell[0], cell[1])
def set_block(col : int, row : int, is_block : bool):
    if type(is_block) is not bool:
        pass
    _crnt_map[row][col] = is_block

def check_collision_vectors(vectors : list[Vector2]):
    for vector in vectors:
        if get_block(*get_cell(vector)) == True:
            return True
    return False

# end is inclusive
def get_sliced_map(start_x, start_y, end_x, end_y):
    if start_x < 0:
        start_x = 0
    if end_x >= X_CELL_COUNT:
        end_x = X_CELL_COUNT - 1
    if start_y < 0:
        start_y = 0
    if end_y >= Y_CELL_COUNT:
        end_y = Y_CELL_COUNT - 1
    
    return [_crnt_map[i][start_x:end_x + 1] for i in range(start_y, end_y + 1)]

def get_vectors(v1 : Vector2, v2 : Vector2, t=0, max_t=1) -> list[Vector2]:
    max_length = (v2 - v1).get_norm() 
    if max_length <= 0:
        return [v1]

    inc_t = 1 / (max_length * CELL_SIZE)
    result : list[Vector2] = []
    while t <= max_t:
        position = v1.lerp(v2, t)
        result.append(position)
        t += inc_t

    return result


##### Object #####
def get_highest_ground_cell(x, y, max_length = float('inf'), is_cell=False):
    global _crnt_map

    cell_start_col, cell_start_row = int(x), int(y)
    if not is_cell:
        cell_start_col, cell_start_row = get_cell((x, y))
    
    max_length /= CELL_SIZE

    dir_down = True
    if out_of_range_cell(cell_start_col, cell_start_row):
        return False
    elif _crnt_map[cell_start_row][cell_start_col]:
        dir_down = False

    if dir_down:
        for row in range(0, cell_start_row + 1).__reversed__():
            if not out_of_range_cell(cell_start_col, row) and _crnt_map[row][cell_start_col]:
                if (cell_start_row - row) > max_length:
                    break
                return (cell_start_col, row)
    else:
        for row in range(cell_start_row + 1, Y_CELL_COUNT):
            if not out_of_range_cell(cell_start_col, row) and not _crnt_map[row][cell_start_col]:
                if (row - cell_start_row) > max_length:
                    break
                return (cell_start_col, row - 1)

    return False






##### DEBUG #####
def draw_debugs():
    if is_debug_mode():
        for rect in _rect_debug_list:
            draw_rectangle(rect.origin[0], rect.origin[1], rect.origin[0]+rect.width, rect.origin[1]+rect.height)
            del rect
        _rect_debug_list.clear()
        
def draw_debug_cell(cell):
    r = CELL_SIZE//2
    pos = get_pos_from_cell(*cell)
    _rect_debug_list.append(Rect(pos, r, r))
def draw_debug_cells(cells):
    for cell in cells:
        draw_debug_cell(cell)
def draw_debug_vector(vector):
    _rect_debug_list.append(Rect(vector, 1, 1))
def draw_debug_vectors(vectors):
    for vector in vectors:
        draw_debug_vector(vector)
def draw_debug_point(point, size):
    _rect_debug_list.append(Rect(point, size, size))
def draw_debug_rect(rect : Rect):
    _rect_debug_list.append(rect)






##### FILE I/O #####
def read_mapfile(index : int, mode):
    import tank
    global _crnt_map, img_map

    _crnt_map = [[False]*X_CELL_COUNT for col in range(Y_CELL_COUNT)]

    global _img_background, _img_ground
    # Draw empty background
    if index < 0:
        index *= -1
        _img_background = load_image_path('background_' + str(index) + '.png')
        _img_ground = load_image_path('ground_' + str(index) + '.png')
        _img_background.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        return

    _img_background = load_image_path('background_' + str(index) + '.png')
    _img_ground = load_image_path('ground_' + str(index) + '.png')

    fileName = 'map_' + str(index) + '.txt'
    file = open('maps/' + fileName, 'r')

    for rowIdx, row in enumerate(_crnt_map):
        line = file.readline()
        for colIdx, ch in enumerate(line):
            if colIdx >= X_CELL_COUNT:
                break
            _crnt_map[rowIdx][colIdx] = bool(int(ch))

    tank.read_data(file, mode)
    file.close()

    img_map = load_image_path('map_' + str(index) + '.png')
    img_map.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + Y_CELL_MIN)

def save_mapfile():
    import tank
    global _crnt_map

    fileName = 'map_save' + '.txt'
    file = open('maps/' + fileName, 'w')

    for row in _crnt_map:
        for col in row:
            file.write(str(int(col)))
        file.write('\n')

    tank.write_data(file)
    
    file.write(END_OF_LINE)
    file.close()