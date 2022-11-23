from toolkit.psd import *
from toolkit.post_processor import *

class postprocessing():
    PNR = 1
    
    def load_data(self, type, param):
        # type = PCR or IV curve...
        
        if type=="PSD":
            print("INIT PCR CALL")
            
            PSD(self.path, param).plot()
        
        else:
            print("Invalid postprocessing with type " + type)
            raise NotImplementedError
        
    def update_PWL_file(self, *args, **kwargs):
        pass