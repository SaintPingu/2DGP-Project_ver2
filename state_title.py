if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_lobby
import sound

image : Image
font : Font
font_show_count = 0
title_music : Music = None

def enter():
    global image, font
    image = load_image_path('title.png')
    font = load_font_path("Lemon-Regular", 64)

    global font_show_count
    font_show_count = 0

    sound.play_bgm('title', 128)

def exit():
    global image, font
    del image
    del font

def update():
    global font_show_count
    font_show_count = (font_show_count + framework.frame_time) % 1

def draw():
    clear_canvas()
    image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    if font_show_count <= 0.5:
        font.draw(250, 80, "Press Any Key To Start!", (0, 167, 255))

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                framework.quit()
                return
            framework.change_state(state_lobby)


def pause():
    pass
def resume():
    pass