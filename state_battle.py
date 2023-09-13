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
import control

_is_game_over = False
_winner = 0
_is_edit_mode = False

SCENE_STATES = ( "Control", "Fire", "Supply", "Ending" )
map_index = 0

def control_normal():
    control.clear()
    control.add_control('←/→', '좌/우 이동')
    control.add_control('마우스 좌클릭', '포신 고정')
    control.add_control('스페이스 바 누르기', '포탄 속도 조절')
    control.add_control('스페이스 바 떼기', '발사')
    control.add_control(':               ', '')
    control.add_control(': [ 관리자 ]', '')
    control.add_control('ESC', '타이틀로 이동')
    control.add_control('F', '연료 풀로 채우기')
    control.add_control('F1', '디버그/그리기 모드')
    control.add_control('F2', 'UI 숨기기')
    control.add_control('F5', '플레이어 1 폭파')
    control.add_control('F6', '플레이어 2 폭파')

def control_debug():
    control.clear()
    control.add_control('F1', '디버그/그리기 해제')
    control.add_control('F2', '무효화 사각형 표시/해제')
    control.add_control('F3', '구름 활성화/비활성화')
    control.add_control('F5', '맵파일 저장')
    control.add_control('F6', '맵 전체 다시 그리기')
    control.add_control('F7', '바람 방향 재설정')
    control.add_control('F9', '탱크 추가')
    control.add_control('1~3', '탱크 색 변경')


    control.add_control('좌클릭', '블럭 생성')
    control.add_control('우클릭', '블럭 파괴')
    control.add_control('1~9', '블럭 생성/파괴 범위 설정')
    control.add_control('*', '범위 * 2')
    control.add_control('/', '범위 1/2')


def enter():
    control_normal()
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

    control.clear()


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