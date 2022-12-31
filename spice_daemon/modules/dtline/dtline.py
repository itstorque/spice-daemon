import sys

import numpy as np
from enum import Enum

from scipy import constants
from scipy.interpolate import interp1d

from spice_daemon.modules import Module

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/tapers_source")

class dtline(Module):
    
    PINS = ["Zlow", "Zhigh"]
    
    def generate_asy_content(self, LIB_FILE, name):
        
        return f"""Version 4
SymbolType CELL
LINE Normal 5 32 0 32
LINE Normal 80 32 72 32
LINE Normal 71 20 8 20
LINE Normal 71 44 8 44
CIRCLE Normal 5 44 10 20
CIRCLE Normal 69 44 74 20
WINDOW 0 70 72 Right 2
SYMATTR Prefix X
SYMATTR Description Taper Z={self.data["Z"]} t={self.data["t"]} L={self.data["L"]} C={self.data["C"]}
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
PIN 80 32 NONE 0
PINATTR PinName A
PINATTR SpiceOrder 1
PIN 0 32 NONE 0
PINATTR PinName B
PINATTR SpiceOrder 2"""
    
    def lib_code(self, lib, LC=None):
        
        node_number = 0
        
        if LC != None:
            if len(LC[0]) != self.data['num_units']:
                raise Exception("L, C array length doesn't match num_units in _lib_generator_helper in dtline")
        
        for i in range(self.data['num_units']):
            
            node_number += 1
            
            if node_number == 1:
                left_node = f"Zlow"
            else:
                left_node = f"Nt{node_number-1}"
            
            if node_number == self.data['num_units']:
                right_node = f"Zhigh"
            else:
                right_node = f"Nt{node_number}"
            
            if LC != None:
                L, C = LC[0][i], LC[1][i]
            else:
                L, C = self.data["L"], self.data["C"]
            
            lib = self.newline_join(lib, f"L{node_number} {left_node} {right_node} {L} Rser=1e-10 Rpar=0 Cpar=0")
            lib = self.newline_join(lib, f"C{node_number} {right_node} 0 {C} Rpar=0 Cpar=0 Lser=0")
            
        return lib