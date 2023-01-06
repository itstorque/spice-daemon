from PyLTSpice.LTSpice_RawRead import LTSpiceRawRead as read_raw
import matplotlib.pyplot as plt

from spice_daemon.toolkit import Toolkit

class PostProcessor(Toolkit):
    
    def __init__(self, parent, params, **kwargs) -> None:
        self.parent = parent
        self.params = params
    
    def setup(self):    
        # modify tran command
        pass
    
    def post(self):
        # run post processing stuff
        pass
    
    def read(self, trace):
        
        data = read_raw(str(self.path))
        
        # taking the absolute value of time because there is a negative sign randomly...
        # this is probably a bit encoding something for extrapolation? not sure tho...
        return abs(data.get_trace("time").get_wave(0)), data.get_trace(trace).get_wave(0)
        # self.t = data.get_trace("time")
        
    def write(self, time, trace):
        pass # TODO: write RAW output to an LTspice figure
        
class PostProcessorPlot(PostProcessor):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.fig = plt.figure(0)
        
        # plt.ion()
        plt.show(block=False)
        
    def plot(self, *args, **kwargs):
        # self.fig.plot(*args, **kwargs)
        
        # if self.fig == None:
        #     plt.plot()
        
        if self.params["gui"]:
            # plt.show()
            plt.draw()
            plt.pause(.001)