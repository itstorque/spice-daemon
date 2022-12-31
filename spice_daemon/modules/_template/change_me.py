import sys

import numpy as np
from enum import Enum

from spice_daemon.modules import Module

class change_me(Module):
    
    PINS = ["IN", "OUT"]
    
    def update_PWL_file(self):
        return None
    
    def lib_code(self, lib="", LC=None):
        
        lib = self.newline_join(lib, f"+ SOURCE CODE FOR LIB ADDED")
            
        return lib
    
    def generate_asy_content(self, LIB_FILE, name):
        # return symbol file text
        
        DESCRIPTION = f"Empty symbol for class {self.__class__.__name__}"
        
        return f"""Version 4
SymbolType CELL
LINE Normal 0 80 0 72
LINE Normal 0 0 0 8
CIRCLE Normal -32 8 32 72
TEXT 0 40 Center 0 {name}
SYMATTR Prefix X
SYMATTR Description {DESCRIPTION}
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
PIN 0 0 NONE 8
PINATTR PinName in
PINATTR SpiceOrder 1
PIN 0 80 NONE 8
PINATTR PinName out
PINATTR SpiceOrder 2
"""