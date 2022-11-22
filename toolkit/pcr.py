from toolkit.post_processor import PostProcessorPlot

import matplotlib.pyplot as plt

class PSD(PostProcessorPlot):
    
    def __init__(self, path, params) -> None:
        self.path = path
        self.params = params
    
    def plot(self):
        
        X = self.read(self.params["trace"])
        
        print(X)
        
        plt.psd(X)
        
        if self.params["gui"]:
            plt.show()