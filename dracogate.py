from tkinter import *
from tkinter import ttk

from aenir2.name_lists import game_title_dict
from aenir2.quintessence import Morph

class Limstella:
    def __init__(self):
        self.unit_parameters={}
        self.hm_parameters={}
        self.auto_parameters={}
        self.misc_parameters={}
        self.edit_history={}
        self.info_variables=self.unit_parameters,\
                             self.hm_parameters,\
                             self.auto_parameters,\
                             self.misc_parameters,\
                             self.edit_history
        self.my_unit=None

    def __del__(self):
        for var in self.info_variables:
            var.clear()
        self.my_unit=None

    def __bool__(self):
        #   Tells user factory-resetted via __del__ call
        return self.my_unit is None and not any(self.info_variables)

    def __len__(self):
        return len(self.edit_history)

    def __call__(self):
        #   Main routine here; save for very end.
        return
