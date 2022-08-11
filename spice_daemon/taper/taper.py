from ..yaml_interface import *

import numpy as np
from enum import Enum

from scipy import constants
from scipy.interpolate import interp1d

from tapers_source.taper_helpers.erickson_taper import length, erickson_polynomial_z
from tapers_source.taper_helpers.klopfenstein_taper import klop_length, klopfenstein_z
from tapers_source.taper_helpers.taper_library import *

class TAPER_GEOM(Enum):
    Erickson = 0
    Klopfenstein = 1

class taper(Element):
    
    def generate_asy_content(self, LIB_FILE, name):
        
        return f"""Version 0
SymbolType BLOCK
LINE Normal -32 -4 -32 4
LINE Normal 36 -24 36 24
LINE Normal 36 0 48 0
LINE Normal -48 0 -32 0
ARC Normal -132 4 48 88 36 0 -36 -8
ARC Normal -132 -88 48 -4 -36 8 36 0
SYMATTR Prefix X
SYMATTR Description {type.lower()} noise source
SYMATTR SpiceModel {name}
SYMATTR ModelFile {LIB_FILE}
PIN 48 0 NONE 8
PINATTR PinName in
PINATTR SpiceOrder 1
PIN -48 0 NONE 8
PINATTR PinName out
PINATTR SpiceOrder 2"""

    def lib_generator(self, NOISE_FILE_DEST_PREAMBLE):
    
        return f"""
"""

    def generate_taper(self, Zin, Zout, type="klopf"):
        
        return 
        
        z_file = 'sonnet_csvs/Z_STO_NbN80pH_sweep.csv'
        eps_file = 'sonnet_csvs/eEff_STO_NbN80pH_sweep.csv'
        
        if type=="klopf": taper_geometry = TAPER_GEOM.Klopfenstein
        elif type=="erikson": taper_geometry = TAPER_GEOM.Erickson
        else: raise NotImplementedError
        
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
        
        w_design = wsim_interp(Z_target)
        
        