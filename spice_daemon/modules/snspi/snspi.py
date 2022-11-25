from spice_daemon.modules import Module

class snspi(Module):
    def generate_asy_content(self, filepath, filename, params=None):
        pass 

    def lib_generator(self, name, params):
        phase_velocity = params['phase_velocity'] # speed of light in material [m/s]
        length = params['length'] # total length of device [m]
        num_pixels = params['num_pixels'] # number of discrete pixels in device
        snpsd_params = params['snspd_params'] # SNSPD parameters (see generate_pixels)

        lib_string = f""".subckt {name} t1 t2
*** SNSPI Definition ***
R1 t1 bv1 50
R2 t2 bv2 50
"""
        nodes_per_pixel = 2
        for pixel in range(num_pixels):
            node1 = pixel*nodes_per_pixel
            node2 = pixel*nodes_per_pixel + 1
            name = 'SNSPD'+str(pixel)
            snspd_statement = self.generate_pixels(snpsd_params, node1, node2, name='XU'+str(pixel))
            ibias = f""" """

    def generate_pixels(self, params, node1, node2, name):
        Lind = params['Lind'] # kinetic inductance of NW [H]
        width = params['width'] # width of NW [m]
        thickness = params['thickness'] # thickness of film [m]
        sheetRes = params['sheetRes'] # normal sheet resistance [ohms]
        Tc = params['Tc'] # transition temp [K]
        Tsub = params['Tsub'] # operating substrate temp [K]
        Jc = params['Jc'] # critical current density [A]
        C = params['C'] # constriction factor

        gate_name = 'SNSPI'+str(node1).zfill(5)
        source_name = 'SNSPI'+str(node2).zfill(5)

        snspd_string = f"""{name} {gate_name} 0 {source_name} 0 nanowireDynamic 
+ Lind={Lind} width={width} thickness={thickness}
+ sheetRes={sheetRes} Tc={Tc} Tsub={Tsub} Jc={Jc}
+ C={C}"""

        return snspd_string