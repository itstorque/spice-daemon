import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from scipy import constants
from scipy.interpolate import interp1d
from phidl import quickplot as qp
from phidl import Device
from enum import Enum

import csv

import skrf as rf

from taper_helpers.erickson_taper import length, erickson_polynomial_z
from taper_helpers.klopfenstein_taper import klop_length, klopfenstein_z
from taper_helpers.taper_library import *
from taper_helpers.git_parts_library import CPW_taper, cpw_pad
from taper_helpers.rf_plots import input_impedance, return_loss

'''1. Setup: obtain simulation data; set calculation parameters
'''

# name to write gds file to
gds_name = 'sto.gds'

# select what kind of taper to write, 0 = Erickson; 1= Klopfenstein
class TAPER_GEOM(Enum):
    Erickson = 0
    Klopfenstein = 1

taper_geometry = TAPER_GEOM.Erickson

z_file = 'sonnet_csvs/Z_STO_NbN80pH_sweep.csv'
eps_file = 'sonnet_csvs/eEff_STO_NbN80pH_sweep.csv'

# set calculation parameters

# geometric params
bending_radius_factor = 3
gap = 1 # [um]
w0 = 0.1 # initial width of device [um]
lmax = 2500 # maximum length before turning [um]
N = 2 # polynomial order for Erickson taper
sections = 6000 # number of sections

# design frequencies
Fc = 500 # lower cut-off frequency [MHz]
F1 = 50 # start frequency for response plot [MHz]
F2 = 20000 # stop frequency for response plot [MHz]
num_freq_points = 1000

# matching params
epsilon2 = constants.epsilon_0*10
Zmatch = 51

# must set this if using Klopfenstein taper!
RdB = -20 # operating band ripple [dB]

# read Z(w), eps(w) directly from Sonnet CSVs
wsim, Zsim, gs = read_sonnet_csv(z_file)
wsim, epssim, gs = read_sonnet_csv(eps_file)

# compute derived parameters
f = Fc*1e6 # design frequency [Hz]
lambdafs = constants.c/f # design free space wavelength [m]

freqs = np.arange(F1*1e6, F2*1e6, (F2-F1)*1e6/num_freq_points)

'''2: Interpolations: form continuous functions from simulated parameters,
compute taper widths
'''

# compute simulated Zload based on width
Zsim_interp = interp1d(wsim, Zsim)
wsim_interp = interp1d(Zsim, wsim)
nsim_interp = interp1d(Zsim, np.sqrt(epssim))
Zload = Zsim_interp(w0)

# compute desired Z(l), n(l), w(l)
if taper_geometry == TAPER_GEOM.Erickson:
    # compute Erickson taper Zs and total length
    Z_target = np.asarray([erickson_polynomial_z(xi, N, Z1=Zmatch, Z2=Zload) for xi in np.arange(0, 1, 1/sections)])
    total_length = length(lambdafs, epsilon2, N) # [m]
elif taper_geometry == TAPER_GEOM.Klopfenstein:
    # compute Klopfenstein taper Zs and total length
    Z_target = np.asarray([klopfenstein_z(xi, RdB, Z1=Zmatch, Z2=Zload) for xi in np.arange(0, 1, 1/sections)])
    total_length = klop_length(lambdafs, Zload, Zmatch, RdB)


dlmd0 = total_length/sections # length per section [m]

'''plt.plot(Z_target)
plt.show()'''

ZL_freq = np.asarray(input_impedance(Zmatch, Z_target[0], 0, freqs))
Zinline_freq = [ZL_freq]
for i in range(num_freq_points):
    Zinline_freq.append(input_impedance(Z_target[i+1], Zinline_freq[i], dlmd0, freqs))
Zin_freq = Zinline_freq[-1]

# TODO find out how to use scikit-rf to generate loss and Smith chart plots
# these charts are currently completely wrong
'''term_losses = [return_loss(zi, Zmatch) for zi in ZL_freq]
input_losses = [return_loss(zi, Zmatch) for zi in Zin_freq]
plt.plot(freqs, term_losses)
plt.show()

rf.plotting.plot_smith(ZL_freq)
rf.plotting.plot_smith(Zin_freq)
plt.show()'''

Z_target = np.flip(Z_target)

n_target = nsim_interp(Z_target)
w_design = wsim_interp(Z_target)

print(w_design)

# divide up length of taper into sections of size dlmd0/n(i) in um
dlmd0_um = dlmd0*1E6 # [um]
l = [0] # [um]
for i in range(1, len(n_target)):
    l.append(l[i-1] + dlmd0_um/n_target[i-1])

num_squares = np.sum(np.divide(dlmd0_um, np.multiply(n_target, w_design)))
print(num_squares)

w_l = interp1d(l, w_design)
n_w = interp1d(w_design, n_target)

''' 3: Taper calculation: compute x and y coordinates of taper
'''

coords, row = generate_coords(l, w_design, w_l, n_w, gap, dlmd0_um, lmax=lmax)
top_pigtail_coords = generate_pigtail(coords, 0, gap)

# check if row even or odd for pigtail geometry calculation
if row % 2 == 1:
    sgn = 1
else:
    sgn = -1

bottom_pigtail_coords = generate_pigtail(coords, -1, gap, sgn=sgn)

coords.add_top_pigtail(top_pigtail_coords)
coords.add_bottom_pigtail(bottom_pigtail_coords, sgn)

d = CPW_taper(coords)
d.write_gds(gds_name)

plt.plot(np.multiply(coords.x0, 1E-3), np.multiply(coords.y0, 1E-3), marker=',')
plt.plot(np.multiply(coords.x1, 1E-3), np.multiply(coords.y1, 1E-3), marker=',', color='orange')
plt.plot(np.multiply(coords.x2, 1E-3), np.multiply(coords.y2, 1E-3), marker=',', color='green')
plt.plot(np.multiply(coords.x3, 1E-3), np.multiply(coords.y3, 1E-3), marker=',', color='green')
plt.plot(np.multiply(coords.x4, 1E-3), np.multiply(coords.y4, 1E-3), marker=',', color='orange')

plt.xlabel('x [mm]')
plt.ylabel('y [mm]')

plt.axis('square')

plt.show()

'''optional: taper linearly at same impedance
'''



''' optional: Connect two tapers back to back
'''

'''
coords, row = generate_coords(l, w_design, w_l, n_w, gap, dlmd0_um, lmax=lmax)

final_width = np.abs(coords.y3[-1] - coords.y2[-1])

if row % 2 == 1:
    sgn = 1
else:
    sgn = -1

bottom_pigtail_coords = generate_pigtail(coords, -1, gap, sgn=sgn)
coords.add_bottom_pigtail(bottom_pigtail_coords, sgn)

tapers = Device("taper")
d1 = CPW_taper(coords, "connect1", "bottom")
d2 = CPW_taper(coords, "connect2","top")
d2.mirror((0, 0), (1, 0))
d2.mirror((0, 0), (0, 1))
upper = tapers.add_ref(d2)
lower = tapers.add_ref(d1)

upper.move(upper.ports["connect2"], lower.ports["connect1"])

pad1 = cpw_pad(final_width, gap, False, final_width/3, final_width, gap)
pad2 = cpw_pad(final_width, gap, False, final_width/3, final_width, gap)
pad1.rotate(180)

top_pad = tapers.add_ref(pad1)
bottom_pad = tapers.add_ref(pad2)

top_pad.move(top_pad.ports["out"], upper.ports["top"])
bottom_pad.move(bottom_pad.ports["out"], lower.ports["bottom"])

tapers.flatten(single_layer=1)
tapers.write_gds(gds_name)'''

# save to .mat for generating coordinates from MATLAB script if desired
# sio.savemat('erickson_nbn.mat', {'erickson_Z': Z_target, 'erickson_l': total_length, 'epssim': epssim, 'wsim': wsim, 'Zsim': Zsim})