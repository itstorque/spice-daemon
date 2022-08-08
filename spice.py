#!/usr/bin/env python3

import argparse
import os
from sys import platform

import numpy as np

from spice_elements import yaml_interface
from spice_elements import *

print(noise_sources)

DAEMON_MAIN_DIR = "spice-daemon"
daemon_filename = "spice-daemon.yaml"

DAEMON_FILE_DEST_PREAMBLE = DAEMON_MAIN_DIR + "/noise_data_"
DAEMON_DEF_FILE = DAEMON_MAIN_DIR + "/" + daemon_filename
LIB_FILE = DAEMON_MAIN_DIR + "/pynoise.lib" 

if __name__=="__main__":
    
    # TODO: add path
    
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-g', '--generate', action='store_true', 
        help="generate noise components to use in circuit design")
   
    parser.add_argument('-n', '--noise', action='store_true', 
        help="launch noise daemon that reloads noise")
    
    parser.add_argument('-s', '--setup', action='store_true', 
        help="setup directory for SPICE noise simulations")
    
    parser.add_argument("file", type=lambda x: yaml_interface.file_path(parser, x), help="LTSpice circuit to launch this script for.")
    
    args = parser.parse_args()
    
    filepath, filename, file_extension = args.file
    
    if platform != "linux":
        # wine doesn't like absolute paths, so just use the relative path noise/
        DAEMON_FILE_DEST_PREAMBLE = filepath + DAEMON_FILE_DEST_PREAMBLE
        DAEMON_DEF_FILE   = filepath + DAEMON_DEF_FILE
        LIB_FILE          = filepath + LIB_FILE
    
    if args.setup:
        print("Setting up directory " + filepath)
        
        os.makedirs(DAEMON_MAIN_DIR, exist_ok=True)
        
        new_file_loc = DAEMON_DEF_FILE
        
        overwrite = True
        
        if os.path.exists(new_file_loc):
            exists_string = daemon_filename + " already exists, type [overwrite] to overwrite otherwise hit enter.\n    > "
            if input(exists_string) == "overwrite":
                overwrite = True
            else:
                overwrite = False
        
        if overwrite:
            with open(new_file_loc, "w") as f:
                f.write("""entropy:
  T: 1
  STEPS: 1000
noise_sources:
  noise_source_1:
    source_type: current
    noise:
      type: gaussian
      mean: 0
      std: 0.0000001
""")
                f.close()
    
    if args.generate == False and args.noise == False and args.setup == False:
        args.generate, args.noise = True, True
    
    if args.generate:
        
        source_data = yaml_interface.load_yaml(DAEMON_DEF_FILE)
        
        lib_content = "** NOISE_Library **\n\n"
        
        STEPS = source_data["sim"]["STEPS"]
        T = source_data["sim"]["T"]
        
        t = np.linspace(0, T, STEPS)
        
        print("Generating new noise component sources...")
        
        for key in source_data.keys():
            
            if key != "sim":
                
                generator = eval(key + "()")
        
                for source in source_data[key].keys():
                
                    lib_content += generator.lib_generator(DAEMON_FILE_DEST_PREAMBLE, source, source_symbol="v" if source_data["noise_sources"][source]["source_type"]=="voltage" else "i")
                    
                    yaml_interface.create_asy(filepath, LIB_FILE, source, element=generator, type=source_data["noise_sources"][source]["source_type"])
            
                yaml_interface.write_lib(LIB_FILE, lib_content)
                
                generator.update_PWL_file(DAEMON_FILE_DEST_PREAMBLE, t)

    if args.noise:
        
        import time, os.path
        
        try:
            seed_time = os.path.getmtime(filepath + filename + ".log")
            
        except FileNotFoundError as e:
            
            if platform == "darwin":
                os.system(f"/Applications/LTspice.app/Contents/MacOS/LTspice -b {filepath}{filename}.{file_extension} & open " + f"{filepath}{filename}.{file_extension}")
                
            else:
                
                print("Could not find log file.")
                print("Make sure that the supplied file exists and make sure it is launched.")
                
                raise FileNotFoundError
            
        seed_time = os.path.getmtime(filepath + filename + ".log")
        yaml_sources_time = os.path.getmtime(DEFAULT_NOISE_DEF_FILE)
        
        print("Launched noise daemon... Use LTSpice normally now :)")
        
        while True:
            
            time.sleep(1)
        
            source_data = yaml_interface.load_yaml(DEFAULT_NOISE_DEF_FILE)
            
            STEPS = source_data["entropy"]["STEPS"]
            T = source_data["entropy"]["T"]
            
            t = np.linspace(0, T, STEPS)
            
            try:
                
                spec_file_change = os.path.getmtime(DEFAULT_NOISE_DEF_FILE) > yaml_sources_time
            
                if os.path.getmtime(filepath + filename + ".log") > seed_time or spec_file_change:
                    
                    seed_time = os.path.getmtime(filepath + filename + ".log")
                    if spec_file_change: yaml_sources_time = os.path.getmtime(DEFAULT_NOISE_DEF_FILE)
                    
                    update_noise(NOISE_FILE_DEST_PREAMBLE, t)
                    
            except FileNotFoundError as e:
                
                if seed_time != None:
                    print("LTSpice closed, killing daemon")
                
                break