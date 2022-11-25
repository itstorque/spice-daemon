# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 12:17:19 2021

@author: Marco Colangelo
"""

# from Mersevey and Tedrow (https://aip.scitation.org/doi/pdf/10.1063/1.1657905)

# from Film-thickness dependence of 10 GHz Nb coplanar-waveguide resonators
# Kunihiro Inomata, Tsuyoshi Yamamoto, Michio Watanabe, Kazuaki Matsuba, and Jaw-Shen 
#Tsai https://avs.scitation.org/doi/pdf/10.1116/1.3232301

import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

width=5e-6
thickness=7e-9
lambda0=232.5e-9
height=50e-9
epsr=7.5

def Lk(width,thickness,lambda0):
    mu0=4*np.pi*1e-7 #H/m
    return mu0/np.pi**2*(lambda0/width)* np.log(4*width/thickness)*np.sinh(thickness/lambda0)/(np.cosh(thickness/lambda0) - 1)

def Z0Microstrip(width, height, epsr): 
    if width/height > 2:
        Z0=377.0/np.sqrt(epsr) *(width/height + 0.883 + (epsr + 1)/(np.pi* epsr)*(np.log(width/(2* height) + 0.94) + 1.451) + 0.165* (epsr - 1)/epsr**2)**(-1)
    else:
        Z0=377.0/(2*np.pi*np.sqrt((epsr + 1)/2))* (np.log(8*height/width) + 1/8 * (width/(2 *height))**2 - 1/2*(epsr - 1)/(epsr + 1)*(np.log(np.pi/2) + 1/epsr *np.log(4/np.pi)))
    return Z0

def epseffMicrostrip(width, height, epsr):
    if width/height > 2:
        def f(x): 
            return np.abs((np.pi/2*width/height - ( x - np.arcsinh(x))))
        a=optimize.minimize(f, x0=1, method="L-BFGS-B")
        c0=np.float(a.x)
        c1 = c0 
        d = 1 + np.sqrt(1 + c1**2)
        q = 1 - 1/d*np.log((d + c1)/(d - c1)) + 0.732/d/epsr*(np.log((d + c1)/(d - c1)) -np.arccosh((0.358*d + 0.595)) + (epsr - 1)/d/epsr*(0.386 - 1/(2*(d - 1))))
        epseff = (1 - q) + q*epsr
        
    else: 
        epseff = (epsr + 1)/2 + (epsr - 1)/2* (np.log(np.pi/2) + 1/epsr*np.log(4/np.pi))/np.log(8*height/width)
    return epseff


def Z0MicrostripKinetic(width, height, epsr, thickness,lambda0): 
   c = 2.998e9
   epsiloneff0 = epseffMicrostrip(width, height, epsr)
   Zchar0 = Z0Microstrip(width, height, epsr)
   L0 = (np.sqrt(epsiloneff0)* Zchar0)/c
   C0 = np.sqrt(epsiloneff0)/(c* Zchar0)
   Zchar1 = np.sqrt((L0 + Lk(width, thickness, lambda0)/C0))
   #epsiloneff1 = c**2 * C0* (L0 + Lk(width, thickness, lambda0));
   return Zchar1

def Z0MicrostripKinetic2(width, height, epsr): 
   c = 2.998e9
   epsiloneff0 = epseffMicrostrip(width, height, epsr)
   Zchar0 = Z0Microstrip(width, height, epsr)
   L0 = (np.sqrt(epsiloneff0)* Zchar0)/c
   C0 = np.sqrt(epsiloneff0)/(c* Zchar0)
   Zchar1 = np.sqrt((L0 + 80e-12/width)/C0)
   #epsiloneff1 = c**2 * C0* (L0 + 80e-12/width);
   return Zchar1


def epseffMicrostripKinetic(width, height, epsr, thickness,lambda0): 
   c = 2.998e9
   epsiloneff0 = epseffMicrostrip(width, height, epsr)
   Zchar0 = Z0Microstrip(width, height, epsr)
   L0 = (np.sqrt(epsiloneff0)* Zchar0)/c
   C0 = np.sqrt(epsiloneff0)/(c* Zchar0)
   #Zchar1 = np.sqrt((L0 + Lk(width, thickness, lambda0)/C0));
   epsiloneff1 = c**2 * C0* (L0 + Lk(width, thickness, lambda0))
   return epsiloneff1



