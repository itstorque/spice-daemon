#!/usr/bin/env python3

class Module():
    '''
    Interface defining some necessary functions each 
    SPICE element needs to implement differently
    '''
    
    def __init__(self, parent):
        self.parent = parent
    
    def generate_asy_content(self, filepath, filename, params):
        pass 

    def lib_generator(self, *args, **kwargs):
        pass
    
    def update_PWL_file(self, *args, **kwargs):
        pass
    
    def load_data(self, name, data):
        self.name = name
        self.data = data
        
    def save_noise(self, noise, t):

        with open(self.parent.module_separate_filename(self.name, '.csv'), "w") as f:
        
            # set initial noise to zero to have a consistent DC operating point
            noise[0] = 0

            for i in range(0,len(t)):
                f.write("{:E}\t{:E}\n".format( t[i], noise[i] ))
                
            f.close()
            
    def newline_join(self, s1, s2): 
        return s1 + "\n" + s2