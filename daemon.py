import numpy as np
import matplotlib.pyplot as plt

import os
import sys

from PyLTSpice.LTSpice_RawRead import RawRead
# from PyLTSpice.LTSpiceBatch import SimCommander
# LTC = SimCommander("Batch_Test.asc")

def sigmoid(x):

    sig = np.where(x < 0, np.exp(x)/(1 + np.exp(x)), 1/(1 + np.exp(-x)))
    return sig

class Circuit:
    
    T=100e-3
    delta_t=0.01e-3
    samples = int(T/delta_t)
    
    SPICE_CMD = '/Applications/LTspice.app/Contents/MacOS/LTspice -b '
    
    def __init__(self, netlist_file, params):
        
        self.netlist_file = netlist_file
        
        self.params = params
        
        self.inputs = {}
        
        self.ltr = None
    
    def add_input(self, node, f, t=None):
        
        time = self.time(t)
        
        self.inputs[node] = (f, time)
            
    def time(self, t=None):
        
        # FIND A BETTER WAY TO PRESERVE TIME PERHAPS BY MIN STEP OR SOMETHING...
        # MAYHAPS RESCALE ALL INPUTS?
        
        if t==None:
            self.t = np.linspace(0, self.T, self.samples)
        else:
            self.t = t
            
        return self.t
        
    def run(self, run_time_params={}):
        
        t = self.time()
        
        for input_node in self.inputs:
            with open(input_node + "_input.csv","w") as f:
                input_f = self.inputs[input_node][0]
                for i in range(0,len(t)):
                    f.write("{:E}\t{:E}\n".format( t[i], input_f[i] ))
                f.close()
        
        with open("trancmd.txt","w") as f:
            f.write(".param transtop {:E}\n".format(t[-1]-t[0]))
            f.write(".param transtart {:E}\n".format(t[0]))
            f.write(".param timestep {:E}\n".format(t[1]-t[0]))
            f.close()

        with open("param.txt","w") as f:
            for key in self.params:
                f.write(".param {:s} {:E}\n".format(key, self.params[key]))
            for key in run_time_params:
                f.write(".param {:s} {:E}\n".format(key, run_time_params[key]))
            f.write("\n")
            f.close()
            
        print(self.SPICE_CMD + " {:s}".format(self.netlist_file))
            
        os.system(self.SPICE_CMD + " {:s}".format(self.netlist_file))
        
    def plot(self, node_names="vout", voltage=True):
        
        if type(node_names) == str:
            node_names = [node_names]
        
        if self.ltr == None:
            self.ltr = RawRead("{:s}".format('circuit_test2_oop.raw'))
            
        time = abs(self.ltr.get_trace("time").get_wave(0))
        
        print(time)
        
        if voltage:
            node_names = ["V(" + node_name + ")" for node_name in node_names]
        
        for node_name in node_names:
            plt.plot(time, self.ltr.get_trace(node_name).get_wave(0), label=node_name)#, self.ltr.get_trace("time"))
        
        
        plt.ylabel("Voltage [V]")
        plt.xlabel("time [s]")
        
        plt.legend()
        plt.show()

if __name__=="__main__":
    
    cir = Circuit('circuit_test2_oop.net', params={
                        "C":1e-3,
                        "L":0.01
                    })
    
    input = sigmoid((cir.time())*1000-50)#1/(1+np.exp(-(cir.time()-0.5)*100)) #1/(1 + np.exp(-time))
    
    cir.add_input('vin', input)
    
    cir.run()
    
    cir.plot(['vin', 'vout'])