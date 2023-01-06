# TODO: disabled this during refactoring
import sys

import numpy as np
from enum import Enum

from scipy import constants
from scipy.interpolate import interp1d

# sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/tapers_source")

# from taper_helpers.erickson_taper import length, erickson_polynomial_z
# from taper_helpers.klopfenstein_taper import klop_length, klopfenstein_z
# from taper_helpers.taper_library import *

from spice_daemon.modules import dtline

class TAPER_GEOM(Enum):
    Erickson = 0
    Klopfenstein = 1

class taper(dtline):
    
    def generate_asy_content(self, LIB_FILE, name):
        
        return f"""Version 4
SymbolType BLOCK
LINE Normal -32 -4 -32 4
LINE Normal 36 -24 36 24
LINE Normal 36 0 48 0
LINE Normal -48 0 -32 0
ARC Normal -132 4 48 88 36 0 -36 -8
ARC Normal -132 -88 48 -4 -36 8 36 0
TEXT -32 -16 VLeft 0 Zhigh={self.data["Zhigh"]}
TEXT 32 -36 VLeft 0 Zlow={self.data["Zlow"]}
SYMATTR Prefix X
SYMATTR Description {self.data['type'].capitalize()} Impedance Matched Taper
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
PIN 48 0 NONE 8
PINATTR PinName in
PINATTR SpiceOrder 1
PIN -48 0 NONE 8
PINATTR PinName out
PINATTR SpiceOrder 2"""

    def lib_generator(self, NOISE_FILE_DEST_PREAMBLE):
        
        # TODO: remove resistance of L, C
        
        lib = self.newline_join(f".subckt {self.name} Zlow Zhigh", "** TAPER **")
        
        LC = self.generate_taper(self.data["Zlow"], self.data["Zhigh"], type=self.data["type"])
        
        return self._lib_generator_helper(lib, LC=LC)

    def generate_taper(self, Zin, Zout, type="klopf"):
        
        z_file   = self.data["z_file"]#'spice_daemon/taper/tapers_source/sonnet_csvs/Z_STO_NbN80pH_sweep.csv'
        eps_file = self.data["eps_file"]#'spice_daemon/taper/tapers_source/sonnet_csvs/eEff_STO_NbN80pH_sweep.csv'
        
        if type=="klopf": taper_geometry = TAPER_GEOM.Klopfenstein
        elif type=="erikson": taper_geometry = TAPER_GEOM.Erickson
        else: raise NotImplementedError
        
        if self.data['type'] == 'erikson':
            N = self.data['erikson_poly_order'] # polynomial order for Erickson taper
        sections = self.data['num_units'] # number of sections

        # design frequencies
        Fc = self.data['Fc'] # lower cut-off frequency [MHz]

        # matching params
        epsilon2 = constants.epsilon_0*10
        Zmatch = Zin

        # must set this if using Klopfenstein taper!
        RdB = self.data['klopf_op_band_ripple'] # operating band ripple [dB]

        # read Z(w), eps(w) directly from Sonnet CSVs
        wsim, Zsim, gs = read_sonnet_csv(z_file)
        wsim, epssim, gs = read_sonnet_csv(eps_file)

        # compute derived parameters
        f = Fc*1e6 # design frequency [Hz]
        lambdafs = constants.c/f # design free space wavelength [m]

        # freqs = np.arange(F1*1e6, F2*1e6, (F2-F1)*1e6/num_freq_points)
        
        # compute simulated Zload based on width
        Zsim_interp = interp1d(wsim, Zsim)
        # wsim_interp = interp1d(Zsim, wsim)
        nsim_interp = interp1d(Zsim, np.sqrt(epssim))
        Zload = Zout # Zsim_interp(w0)

        # compute desired Z(l), n(l), w(l)
        if taper_geometry == TAPER_GEOM.Erickson:
            # compute Erickson taper Zs and total length
            Z_target = np.asarray([erickson_polynomial_z(xi, N, Z1=Zmatch, Z2=Zload) for xi in np.arange(0, 1, 1/sections)])
            total_length = length(lambdafs, epsilon2, N) # [m]
        elif taper_geometry == TAPER_GEOM.Klopfenstein:
            # compute Klopfenstein taper Zs and total length
            Z_target = np.asarray([klopfenstein_z(xi, RdB, Z1=Zmatch, Z2=Zload) for xi in np.arange(0, 1, 1/sections)])
            total_length = klop_length(lambdafs, Zload, Zmatch, RdB)


        # dlmd0 = total_length/sections # length per section [m]
        
        if Z_target[0] > Z_target[-1]:
            Z_target = np.flip(Z_target)
        
        n_target = nsim_interp(Z_target)
        
        v_target = n_target * constants.c
        
        L = Z_target / v_target / self.data['num_units']
        C = 1 / (Z_target * v_target) / self.data['num_units']
        
        print("WOOT")
        print(L, C)
        
        return L, C