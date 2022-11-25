import numpy as np
import colorednoise as cn
from scipy import constants

from spice_daemon.modules import noise_sources

class noisy_resistor(noise_sources):
    
    def generate_asy_content(self, LIB_FILE, name):
        
        return f"""Version 4
SymbolType CELL
LINE Normal 16 88 16 96
LINE Normal 0 80 16 88
LINE Normal 32 64 0 80
LINE Normal 0 48 32 64
LINE Normal 32 32 0 48
LINE Normal 16 16 16 24
LINE Normal 16 24 32 32
LINE Normal -12 52 -16 60
LINE Normal -12 52 -20 52
LINE Normal -12 68 -16 76
LINE Normal -12 68 -20 68
LINE Normal -12 36 -16 44
LINE Normal -12 36 -20 36
ARC Normal -44 40 -28 56 -28 48 -44 44
ARC Normal -28 40 -12 56 -28 48 -12 52
ARC Normal -44 56 -28 72 -28 64 -44 60
ARC Normal -28 56 -12 72 -28 64 -12 68
ARC Normal -44 24 -28 40 -28 32 -44 28
ARC Normal -28 24 -12 40 -28 32 -12 36
WINDOW 0 36 40 Left 2
WINDOW 3 36 76 Left 2
SYMATTR Prefix X
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
SYMATTR Description Johnson Noise Resistor
PIN 16 16 NONE 0
PINATTR PinName A
PINATTR SpiceOrder 1
PIN 16 96 NONE 0
PINATTR PinName B
PINATTR SpiceOrder 2
"""

    def lib_generator(self, NOISE_FILE_DEST_PREAMBLE):

        return f""".subckt {self.name} A B

** NOISE SOURCE **
V temp A PWL file={NOISE_FILE_DEST_PREAMBLE}{self.name}.csv
R B temp {self.data["resistance"]}

.ends {self.name}

"""
    
    def update_PWL_file(self, NOISE_FILE_DEST_PREAMBLE, t):
        
        vn = np.sqrt(4 * constants.k * self.data["temperature"] * self.data["resistance"] * self.data["bandwidth"])
        
        noise = np.random.normal(0, vn, len(t))
        
        return self.save_noise(NOISE_FILE_DEST_PREAMBLE, noise, t)