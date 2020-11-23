from tkinter import *
from tkinter import ttk

from aenir2.name_lists import game_title_dict

root=Tk()
root.title('Please select a game')
mainframe=ttk.Frame(root)
mainframe.grid()
d=game_title_dict()
lvar=tuple(d.keys())
s=StringVar(value=lvar)
lbox=Listbox(mainframe,listvariable=s)
lbox.grid()

def bind_func(*args):
    global d
    key=lbox.selection_get()
    print(d[key])

lbox.bind('<Return>',bind_func)
lbox.focus()
btnkw={
    'text':'Quit',\
    'command':lambda *args: root.destroy()
    }
button=ttk.Button(mainframe,**btnkw)
button.grid()

root.mainloop()
