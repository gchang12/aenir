from tkinter import *
from tkinter import ttk

from aenir2.gui_tools import *
from aenir2.quintessence import Morph

class Limstella:
    def __init__(self):
        self.unit_params={}
        self.hm_params={}
        self.auto_params={}
        self.misc_params={}
        self.display_params={}
        self.edit_history={}
        self.info_variables=self.unit_params,\
                             self.hm_params,\
                             self.auto_params,\
                             self.misc_params,\
                             self.display_params,\
                             self.edit_history
        self.my_unit=None

    def __del__(self):
        for var in self.info_variables:
            var.clear()
        self.my_unit=None

    def __bool__(self):
        #   Tells user if factory-resetted via __del__ call
        return self.my_unit is None and not any(self.info_variables)

    def __call__(self):
        #   Main routine here; save for very end.
        return

if __name__ == '__main__':
    x=Limstella()
    y=not x
    print(y)
