import spice_daemon as sd

sim = sd.Simulation("test/circuit.asy", T=1, STEPS=1000)

sim.run_watchdog()