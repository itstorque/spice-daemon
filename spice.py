import spice_daemon as sd

# sim = sd.Simulation("./test2/init2.asc")

sim = sd.new("test2/testCreate.asc")

# sim.setup()

sim.launch_ltspice()

sim.run_watchdog()