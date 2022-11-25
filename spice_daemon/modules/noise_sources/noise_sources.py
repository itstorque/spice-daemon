import numpy as np
import colorednoise as cn

import spice_daemon.helpers as sdh

class noise_sources(sdh.Element):
    
    def generate_asy_content(self, LIB_FILE, name):
        
        type = self.data['source_type']
    
        # draw top right glyph indicatin directionality and
        # V or I source
        if type=="current":
            accent = """LINE Normal 32 0 32 16
LINE Normal 32 0 36 8
LINE Normal 32 0 28 8"""
        elif type=="voltage":
            accent = """LINE Normal 32 0 32 8
LINE Normal 28 4 36 4
LINE Normal 28 16 36 16"""
        else: 
            raise TypeError
        
        # actual file content
        return f"""Version 4
SymbolType CELL
LINE Normal 0 80 0 72
{accent}
LINE Normal 0 0 0 8
CIRCLE Normal -32 8 32 72
TEXT 0 40 Center 0 {name}
SYMATTR Prefix X
SYMATTR Description {type.capitalize()} Noise Source
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
PIN 0 0 NONE 8
PINATTR PinName in
PINATTR SpiceOrder 1
PIN 0 80 NONE 8
PINATTR PinName out
PINATTR SpiceOrder 2
"""

    def lib_generator(self):#, name, source_symbol="V"):
        
        source_symbol = "v" if self.data['source_type'] == "voltage" else "i"
    
        return f""".subckt {self.name} in out

** NOISE SOURCE **
{source_symbol} out in PWL file={self.parent.module_separate_filename(self.name, '.csv')}

.ends {self.name}

"""
        
    def update_PWL_file(self, t):
                
        noise_data = self.data["noise"]
        
        if noise_data["type"] == "gaussian":
            
            noise = np.random.normal(noise_data["mean"], noise_data["std"], len(t))
            
        elif noise_data["type"] == "poisson":
            
            noise = noise_data["scale"] * np.random.poisson(noise_data["lambda"], len(t))
            
        elif noise_data["type"] == "one_over_f":
            
            noise = noise_data["scale"] * cn.powerlaw_psd_gaussian(noise_data["power"], len(t), fmin=noise_data["fmin"])
            
        elif noise_data["type"] == "custom":
            
            # This definition is not redundant. `.yaml` file can define
            # custom expressions that generate noise for N steps
            # and this needs to be defined here for the eval command.
            N = len(t)
        
            noise = eval(noise_data["command"])
        
        else:
            print("Wrong noise type defined in .yaml file")
            raise TypeError
        
        return self.save_noise(noise, t)