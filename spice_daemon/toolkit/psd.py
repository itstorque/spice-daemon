import spice_daemon.toolkit as sdt

import matplotlib.pyplot as plt

from scipy.signal import welch
import scipy.fftpack
import numpy as np

from PyLTSpice.LTSpice_RawWrite import Trace, LTSpiceRawWrite as ltwrite

class PSD(sdt.PostProcessorPlot):
    
    def __init__(self, *args, **kwargs) -> None:
        
        self.X = 0
        
        super().__init__(*args, **kwargs)
    
    def plot(self):
        
        print(">>>>", self.params)
        
        print(self.read(self.params["trace"]))
        
        tp, Xp = self.read(self.params["trace"])
        
        # print(tp)
        
        N=100_000
        
        t = np.linspace(tp[0], tp[-1]*100, N)
        
        print(t)
        
        # X = np.sin(20e6 * 2.0*np.pi*t)#
        X = np.interp(t, tp, Xp)
        
        # plt.plot(t, X)
        
        # yf = scipy.fftpack.fft(X)
        # xf = np.linspace(0.0, 1.0/(t[1]-t[0]), N//2)

        plt.clf()
        # plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))

        
        # plt.clf()
        
        plt.psd(X, Fs=1/(t[1]-t[0]), figure=self.fig, sides="twosided")
        # F = 1000e6
        # plt.xlim([-F, F])
        
        super().plot()
        
        
        # f, Y = welch(X)
        
        # plt.plot(f, Y)
        
        # super().plot()
        
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