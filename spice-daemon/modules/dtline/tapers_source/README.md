# tapers

## Main ##
- taper_script.py: run this to generate plots and coordinates
  for impedance matching tapers. select between taper geometries
  and other parameters at the top of the script

## Helpers ##
- taper_library.py: helper classes and functions for generating
  gds coordinates for any impedance matching taper based on Sonnet
  simulations

- erickson_taper.py: provides helper functions for computing 
  impedance as a function of length for an Erickson taper

- erickson_nbn.mat: generates plots and coordinates for Erickson
  impedance matching taper in MATLAB. run after taper_script.py
  if desired

- klopfenstein_taper.py: provides helper functions for computing 
  impedance as a function of length for a Klopfenstein taper
