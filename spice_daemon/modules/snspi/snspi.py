import sys

import numpy as np
from enum import Enum

from spice_daemon.modules import Module, Element

class snspi(Module):
    
    PINS = ["N0", "OUT"]
    
    def update_PWL_file(self):
        return None
    
    def lib_code(self, lib="", LC=None):
        # example vars from yaml file: - these are stored in self.data['num_units']
            # num_units: 1000
            # L: 10e-7
            # C: 8e-9
            # ic: 20
            # incident_photons:
            #   30: 20e-9, 100e-9
            #   60: 10e-9
            
        N = self.data['num_units']
        photon_locations = self.data['incident_photons']
        ic, Lind = self.data["ic"], self.data["L"]
        Cap = self.data["C"]
        
        for i in range(N):
            
            # if there is a photon coming on this wire, one of the terminals is attached to
            # a non-linear source
            PHOTON_LOC = 0
            if i+1 in photon_locations.keys(): 
                PHOTON_LOC = f"PHOTON{i}"
                k=0
                for t in photon_locations[i+1].split(","):
                    k+=1
                    t=float(t)
                    lib += Element.photon_spike(f"{k}_at_{i}", PHOTON_LOC, t)
                
            left_node, right_node = f"N{i}", f"N{i+1}" if i+1!=N else "OUT"

            lib += Element.nanowire(i, left_node, right_node, PHOTON_LOC, 0, ic, Lind) # spice code to hook nanowire between nodes i and i+1... photon inputs at PHOTONi and ground
            lib += Element.capacitor(i, left_node, 0, Cap)
            
        # terminate with cap to ground
        lib += Element.capacitor(N, "OUT", 0, Cap)
            
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