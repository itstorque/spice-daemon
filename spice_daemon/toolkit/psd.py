import spice_daemon.toolkit as sdt

import matplotlib.pyplot as plt

from scipy.signal import welch
import numpy as np

from PyLTSpice.LTSpice_RawWrite import Trace, LTSpiceRawWrite as ltwrite

class PSD(sdt.PostProcessorPlot):
    
    def __init__(self, path, params) -> None:
        self.path = path
        self.params = params
        
        self.X = 0
        
        super().__init__()
    
    def plot(self):
        
        t, X = self.read(self.params["trace"])
        
        plt.clf()
        
        # plt.psd(X, figure=self.fig)
        
        # super().plot()
        
        f, Y = welch(X)
        
        plt.plot(f, Y)
        
        super().plot()
        
        # f = Trace("frequency", f)
        # Y = Trace("N001", Y)
        
        # ltfig = ltwrite()
        # ltfig.add_trace(f)
        # ltfig.add_trace(Y)
        
        # print(self.path+".fft")
        
        # ltfig.save(self.path+".fft")
        
        # LW = ltwrite()
        # tx = Trace('time', np.arange(0.0, 3e-3, 997E-11))
        # vy = Trace('N001', np.sin(2 * np.pi * tx.data * 10000))
        # vz = Trace('N002', np.cos(2 * np.pi * tx.data * 9970))
        # LW.add_trace(tx)
        # LW.add_trace(vy)
        # LW.add_trace(vz)
        # LW.save(self.path+".raw")