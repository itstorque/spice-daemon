import matplotlib.pyplot as plt

class PostProcessor:
    
    def __init__(self, path) -> None:
        pass
    
    def setup(self):    
        # modify tran command
        pass
    
    def post(self):
        # run post processing stuff
        pass
    
    def read(self):
        pass
        
class PostProcessorPlot(PostProcessor):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.fig = plt.figure()
        
    def plot(self, *args, **kwargs):
        self.fig.plot(*args, **kwargs)