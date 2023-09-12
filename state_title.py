if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_lobby
import sound
import random

image : Image
font : Font
font_show_count = 0
title_music : Music = None
logo : Image


class Border():
    def __init__(self, image : Image):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.image = image
        self.alpha = 0
        self.inc = True
    
    def update(self):
        if self.inc:
            self.alpha += framework.frame_time * 0.25
            if self.alpha >= 1:
                self.alpha = 1
                self.inc = False
        else:
            self.alpha -= framework.frame_time * 0.75
            if self.alpha <= 0:
                self.alpha = 0
                self.inc = True
        self.image.opacify(self.alpha)

    def draw(self):
        self.image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

border : Border







def enter():
    global image, font
    image = load_image_path('title.png')
    font = load_font_path("Lemon-Regular", 64)

    global font_show_count
    font_show_count = 0

    global image_border, border
    image_border = load_image_path('title_border.png')
    border = Border(image_border)

    global logo
    logo = load_image_path('logo.png')

    sound.play_bgm('title', 128)

def exit():
    global image, font, border
    del image
    del font
    del border

def update():
    global font_show_count
    font_show_count = (font_show_count + framework.frame_time) % 3

    border.update()

def draw():
    clear_canvas()
    image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    border.draw()

    logo.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    if font_show_count <= 2:
        #font.draw(250, 80, "Press Any Key To Start!", (0, 167, 255))
        font.draw(250, 80, "Press Any Key To Start!", (191, 191, 191))

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