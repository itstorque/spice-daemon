#!/usr/bin/env python3

import spice_daemon as sd
import sys

# sd.Simulation("")

# sim = sd.Simulation("./test2/init2.asc")

import matplotlib.pyplot as plt

plt.figure()

print("Running spice-daemon on Simulation: " + sys.argv[1])

sim = sd.Simulation(sys.argv[1])

# sim.setup()

sim.launch_ltspice()

sim.run_watchdog()