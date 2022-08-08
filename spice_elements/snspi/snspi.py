from ..yaml_interface import *

class snspi(Element):
    def generate_asy_content(self, filepath, filename, params=None):
        pass 

    def lib_generator(self, params):
        phase_velocity = params['phase_velocity'] # speed of light in material [m/s]
        length = params['length'] # total length of device [m]
        num_pixels = params['num_pixels'] # number of discrete pixels in device
        snpsd_params = params['snspd_params'] # SNSPD parameters (see generate_pixels)

        snspd_statement = self.generate_pixels(snpsd_params)

    def generate_pixels(self, params):
        Lind = params['Lind'] # kinetic inductance of NW [H]
        width = params['width'] # width of NW [m]
        thickness = params['thickness'] # thickness of film [m]
        sheetRes = params['sheetRes'] # normal sheet resistance [ohms]
        Tc = params['Tc'] # transition temp [K]
        Tsub = params['Tsub'] # operating substrate temp [K]
        Jc = params['Jc'] # critical current density [A]
        C = params['C'] # constriction factor