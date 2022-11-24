import numpy as np

def input_impedance(Z0, ZL, l, freqs, er=1):
    ''' computes input impedance of a lossless transmission line for given
    design parameters. see http://rfic.eecs.berkeley.edu/~niknejad/ee117/pdf/lecture6.pdf
    or https://www.mathworks.com/matlabcentral/fileexchange/22996-rf-utilities-v1-2 trl function

    for our tapers, we treat the impedance at a particular point in the taper as the "load"
    and 50 ohms as the characteristic impedance

    Z0 = characteristic impedance of line
    ZL = load impedance (to be transformed)
    l = line length [m]
    freqs = frequencies at which to compute impedance [Hz]
    er = relative dielectric permittivity at Z0

    returns: input impedance as a function of frequency
    '''
    gamma = 1j*2*np.pi*freqs*er/3E8
    return Z0*(ZL + Z0*np.tanh(gamma*l))/(Z0 + ZL*np.tanh(gamma*l))

def return_loss(Z0, ZL):
    ''' computes return loss at given frequencies based on impedance
    mismatch. see https://www.mathworks.com/matlabcentral/fileexchange/22996-rf-utilities-v1-2
    rlossc function

    for our tapers, the taper impedance is the characteristic impedance here

    Z0 = characteristic impedance of line
    ZL = load impedance

    returns: return loss [dB]
    '''
    P = (ZL - Z0)/(ZL + Z0)
    return 20*np.log10(np.abs(P))