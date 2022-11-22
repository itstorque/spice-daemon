from PyLTSpice.LTSpice_RawRead import LTSpiceRawRead as read_raw
import matplotlib.pyplot as plt

class PostProcessor:
    
    def __init__(self) -> None:
        # self.path is set inside the loop in spice.py
        pass
    
    def setup(self):    
        # modify tran command
        pass
    
    def post(self):
        # run post processing stuff
        pass
    
    def read(self, trace):
        
        data = read_raw(self.path+".raw")
        
        return data.get_trace(trace)
        # self.t = data.get_trace("time")
        
class PostProcessorPlot(PostProcessor):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.fig = plt.figure()
        
    def plot(self, *args, **kwargs):
        self.fig.plot(*args, **kwargs)