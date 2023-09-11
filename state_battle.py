if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_title
import state_lobby
import sound

import object
import gui
import gmap
import tank
import shell
import sprite
import ending
import environment as env
import supply
import inventory

_is_game_over = False
_winner = 0
_is_edit_mode = False

SCENE_STATES = ( "Control", "Fire", "Supply", "Ending" )
map_index = 0

def enter():
    from  state_lobby import get_mode, get_difficulty
    mode = get_mode()

    global scene_state
    scene_state = SCENE_STATES[0]
    
    global map_index
    map_index = state_lobby.crnt_map_index + 1


    import state_challenge_lobby
    if state_challenge_lobby._is_challenge:
        mode = 'PVE'
        difficulty = state_challenge_lobby.get_difficulty()
        map_index = state_challenge_lobby.get_map_index()
    else:
        difficulty = get_difficulty()

    object.enter()
    gmap.enter()
    shell.enter()
    gui.enter()
    tank.enter()
    sprite.enter()
    env.enter(map_index)
    ending.enter()
    sound.enter('battle')
    supply.enter()
    inventory.enter()

    
    gmap.read_mapfile(map_index, mode)
    tank.apply_difficulty(difficulty)

    global _is_game_over
    _is_game_over = False
    
    global _is_edit_mode
    if map_index > 0:
        sound.play_battle_bgm(map_index)
        _is_edit_mode = False
    else:
        _is_edit_mode = True


def exit():
    inventory.exit()
    env.exit()
    sprite.exit()
    shell.exit()
    tank.exit()
    gui.exit()
    object.exit()
    ending.exit()
    gmap.exit()
    sound.exit()
    supply.exit()


def update():
    global _is_game_over, _winner

    object.update()
    sprite.update()
    gui.update()
    tank.update()

    if _is_edit_mode:
        return
    if scene_state == "Ending":
        if _is_game_over == False:
            if _winner == 0:
                sound.play_bgm('win')
            elif _winner == -1:
                sound.play_bgm('lose')
            else:
                assert(0)

        _is_game_over = True
        if ending.update() == False:
            import state_challenge_lobby
            if state_challenge_lobby._is_challenge:
                if ending._winner == 0:
                    state_challenge_lobby._challenge_level += 1
                    if state_challenge_lobby._challenge_level >= 4:
                        state_challenge_lobby._challenge_level = 0
                        framework.change_state(state_title)
                        return
                framework.change_state(state_challenge_lobby)
            else:
                framework.change_state(state_title)

def draw():

    gmap.draw()
    gui.draw()
    inventory.draw()
    object.draw()
    sprite.draw()
    gmap.draw_debugs()

    t = tank.crnt_tank
    if t:
        shell = t.test_shell
        if shell:
            for rect in shell.test_rects:
                gmap.draw_rect(rect)

    if _is_game_over:
        ending.draw(_winner)
    
    update_canvas()

def handle_events(events=None):
    if events == None:
        events = get_events()
    event : Event

    if gmap.is_draw_mode == True:
        gmap.handle_draw_mode_events(events)
        return

    for event in events:
        if event.type == SDL_QUIT:
            framework.change_state(state_title)
            return

        tank.handle_event(event)

        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                gmap.start_draw_mode()
            elif event.key == SDLK_ESCAPE:
                framework.change_state(state_title)

def pause():
    pass
def resume():
    pass


def set_state(state : str):
    assert(state in SCENE_STATES)

    global scene_state
    scene_state = state

def set_winner(winner):
    global _winner
    _winner = winner

def get_gravity():
    gravity = 9.8
    if map_index == 4:
        return gravity * 0.7
    return gravity