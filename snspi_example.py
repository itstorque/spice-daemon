#!/usr/bin/env python3

import argparse
import os
from sys import platform
from numpy import True_
import yaml
import re
from enum import Enum, auto

from spice_daemon.yaml_interface import *
from spice_daemon.snspi.snspi import SNSPI

DEFAULT_SNSPI_DEF_FILE = "spice_daemon/snspi/snspi.yaml"
LIB_FILE = "spice_daemon/snspi/snspi.lib"

class Element_Types(Enum, str):
    SNSPI = 'snspi'

if __name__=="__main__":
    
    # TODO: add path
    
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-g', '--generate', action='store_true', 
        help="generate noise components to use in circuit design")
   
    parser.add_argument('-n', '--noise', action='store_true', 
        help="launch noise daemon that reloads noise")
    
    parser.add_argument('-s', '--setup', action='store_true', 
        help="setup directory for SPICE noise simulations")
    
    parser.add_argument("file", type=lambda x: file_path(parser, x), help="LTSpice circuit to launch this script for.")
    
    args = parser.parse_args()
    
    filepath, filename, file_extension = args.file
    
    if platform != "linux":
        # wine doesn't like absolute paths, so just use the relative path noise/
        DEFAULT_NOISE_DEF_FILE   = filepath + DEFAULT_SNSPI_DEF_FILE
        LIB_FILE                 = filepath + LIB_FILE
    
    if args.setup:
        print("Setting up directory " + filepath)
        
        os.makedirs(filepath + "/spice_daemon/snspi", exist_ok=True)
        
        new_file_loc = filepath + "/spice_daemon/snspi/snspi.yaml"
        
        overwrite = True
        
        if os.path.exists(new_file_loc):
            exists_string = "/spice_daemon/snspi/snspi.yaml already exists, type [overwrite] to overwrite otherwise hit enter.\n    > "
            if input(exists_string) == "overwrite":
                overwrite = True
            else:
                overwrite = False
        
        if overwrite:
            with open(new_file_loc, "w") as f:
                f.write("""elements:
                            snspi_1:
                                element_type: snpsi
                                parameters:
                                    phase_velocity: 0.05*3E8
                                    length: 100E-6
                                    num_pixels: 100
                                    snspd_params:
                                    Lind: 100E-9
                                    width: 100E-9
                                    thickness: 4E-9
                                    sheetRes: 400
                                    Tc: 10.5
                                    Tsub: 2
                                    Jc: 50E9
                                    C: 1
                            """)
                f.close()
    
    if args.generate == False and args.setup == False:
        args.generate = True
    
    if args.generate:
        
        element_data = load_yaml(DEFAULT_SNSPI_DEF_FILE)
        
        lib_content = "** ELements_Library **\n\n"
        
        print("Generating new element library files...")
        
        for element in element_data["elements"].keys():
        
            if element_data["elements"][element]["element_type"] == Element_Types.SNSPI:
                lib_content += SNSPI.lib_generator(element_data["elements"][element]["parameters"])
            
                create_asy(filepath, LIB_FILE, element, SNSPI)
        
        write_lib(LIB_FILE, lib_content)