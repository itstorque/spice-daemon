#!/usr/bin/env python3

import spice_daemon as sd

# sd.Simulation("")

# sim = sd.Simulation("./test2/init2.asc")

sim = sd.new("snspi_test.asc")

# sim.setup()

sim.launch_ltspice()

sim.run_watchdog()