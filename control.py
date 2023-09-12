from tkinter import *
from tkinter.ttk import *
import threading

window = None
canvas = None
text_item = None
string = ''
def app():
    global window, canvas, text_item

    window = Tk()
    window.title("조작키")
    window.geometry('+100+100')
    window.geometry('500x1000')
    window.resizable(False, False)

    from PIL import ImageTk, Image
    image = Image.open('images/' + 'tkinter_back.png')
    bg = ImageTk.PhotoImage(image)

    frame = Frame(window)
    frame.pack()
    canvas = Canvas(window, width=500, height=1000)  # 캔버스 크기를 이미지 크기에 맞게 조절하세요
    canvas.pack()
    canvas.create_image(0, 0, anchor=NW, image=bg)
    text_item = canvas.create_text(50, 50, text=string, font=('Consolas, 32'), anchor=NW)

    window.mainloop()

tkinter_thread = None
def start():
    global tkinter_thread
    tkinter_thread = threading.Thread(target=app)
    tkinter_thread.start()
    

def end():
    global window
    window.quit()

    global tkinter_thread
    tkinter_thread.join()






def add_control(key, comment):
    global string
    string += key + ' : ' + comment + '\n'

    global canvas, text_item
    canvas.itemconfig(text_item, text=string)

def clear():
    global string
    string = ''

    global canvas, text_item
    canvas.itemconfig(text_item, text=string)