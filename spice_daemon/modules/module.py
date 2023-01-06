#!/usr/bin/env python3
import hashlib
import spice_daemon.helpers as sdh

class Element():
    
    def inductor(name, port1, port2, value):
        return f"L{name} {port1} {port2} {value}\n"
    
    def capacitor(name, port1, port2, value):
        return f"C{name} {port1} {port2} {value}\n"
    
    def nanowire(name, port1, port2, photon_in, photon_out, ic, Lind):
        # TODO: implement ic -> Isw is weird, need to make sure its ok to just reset it
        # NOTE: `.lib snspd.lib` is included to make this run
        return f"XU{name} {photon_in} {photon_out} {port1} {port2} nanowireDynamic Lind={Lind}\n.lib snspd.lib\n"
    
    def photon_spike(name, node, time):
        return Element.source(f"photon_{name}", "i", node, 0, f"PULSE(0 1u {time} 1p 1p 1p)")
    
    def source(name, type, port1, port2, value):
        type = type.lower()
        if type == "current": type="i"
        if type == "voltage": type="v"
        if type not in {"i", "v"}:
            raise TypeError("source type can only be i (current) or v (voltage)")
        
        return f"{type}{name} {port2} {port1} {value}\n"
        

class Module():
    '''
    Interface defining some necessary functions each 
    SPICE element needs to implement differently
    '''
    
    PINS = ["IN", "OUT"]
    
    def __init__(self, parent):
        self.parent = parent
        self.name = None
    
    def generate_asy_content(self, LIB_FILE, name):
        pass 
    
    def lib_generator(self):
        
        # TODO: remove resistance of L, C
        
        lib = self.newline_join(f".subckt {self.name} {' '.join(self.PINS)}", f"** {self.__class__.__name__} **\n")
        
        # LC = self.generate_taper(self.data["Zlow"], self.data["Zhigh"], type=self.data["type"])
        # LC = [ [L0, L1, ...] , [C0, C1, ...] ]
        
        temp = self.lib_code()
        line_hashes = set()
        
        for line in temp.split("\n"):
            hash = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
            if hash not in line_hashes:
                lib += line + "\n"
                line_hashes.add(hash)

        return self.newline_join(lib, f".ends {self.name}\n\n")
    
    def update_PWL_file(self, *args, **kwargs):
        pass
    
    def generate_asy(self):
        
        if self.name == None: 
            print("In generate_asy: Module has no name")
            raise NameError()
        
        content = self.generate_asy_content(str(self.parent.lib_file.get_path()), self.name)
        
        asy_file = sdh.File(self.parent.circuit_loc / (self.name + ".asy"), touch=True)
        
        asy_file.write(content)
    
    def generate_asy_content(self, LIB_FILE, name):
        # [Default] return symbol file text
        
        DESCRIPTION = f"Empty symbol for class {self.__class__.__name__}"
        
        return f"""Version 4
SymbolType CELL
LINE Normal 80 0 72 0
LINE Normal 0 0 8 0
RECTANGLE Normal 8 -8 72 8
TEXT 0 -12 Center 0 {self.PINS[0]}
TEXT 80 -12 Center 0 {self.PINS[1]}
TEXT 40 0 Center 0 {name}
SYMATTR Prefix X
SYMATTR Description {DESCRIPTION}
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
PIN 0 0 NONE 8
PINATTR PinName {self.PINS[0]}
PINATTR SpiceOrder 1
PIN 80 0 NONE 8
PINATTR PinName {self.PINS[1]}
PINATTR SpiceOrder 2
"""
    
    def load_data(self, name, data):
        self.name = name
        self.data = data
        
    def save_noise(self, data):
        return self.save_pwl(data)
        
    def save_pwl(self, data):

        with open(self.parent.module_separate_filename(self.name, 'csv'), "w") as f:
        
            # set initial data to zero to have a consistent DC operating point
            data[0] = 0

            for i in range(0,len(self.parent.t)):
                f.write("{:E}\t{:E}\n".format( self.parent.t[i], data[i] ))
                
            f.close()
            
    def newline_join(self, s1, s2): 
        return s1 + "\n" + s2