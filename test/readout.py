from PyLTSpice.LTSpice_RawRead import LTSpiceRawRead as read_raw

data = read_raw("/Users/torque/programs/spice-daemon/test/Draft1.raw")

print(data.get_trace_names())
# print(data.get_raw_property())

IR1 = data.get_trace("V(one_photon)")
t = data.get_trace("time")

print(IR1)

from matplotlib import pyplot as plt
k = 0
steps = data.get_steps()
for step in range(len(steps)):
    # if k%2==1:
    plt.plot(t.get_time_axis(step), IR1.get_wave(step), label=steps[step])
    # k+=1
   
plt.legend()
plt.show()