#!/usr/bin/env python3

import argparse
import os
from sys import platform

import numpy as np

from spice_daemon import yaml_interface
from spice_daemon import *

DAEMON_MAIN_DIR = ".spice-daemon-data"
daemon_filename = "spice-daemon.yaml"

DAEMON_FILE_DEST_PREAMBLE = DAEMON_MAIN_DIR + "/noise_data_"
DAEMON_DEF_FILE = DAEMON_MAIN_DIR + "/" + daemon_filename
LIB_FILE = DAEMON_MAIN_DIR + "/pynoise.lib" 

def update_components(source_data, daemon_file_dest_preamble, t):
    
    lib_content = ""
    
    for key in source_data.keys():
            
        if key != "sim":
            
            generator = eval(key + "()")
    
            for source in source_data[key].keys():
                
                generator.load_data(source, source_data["noise_sources"][source])
            
                lib_content += generator.lib_generator(DAEMON_FILE_DEST_PREAMBLE)
                
                generator.update_PWL_file(DAEMON_FILE_DEST_PREAMBLE, t)
        
            yaml_interface.write_lib(LIB_FILE, lib_content)

if __name__=="__main__":
    
    # TODO: add path
    
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-g', '--generate', action='store_true', 
        help="generate spice daemon components to use in circuit design")
   
    parser.add_argument('-d', '--daemon', action='store_true', 
        help="launch spice daemon that reloads params live")
    
    parser.add_argument('-s', '--setup', action='store_true', 
        help="setup directory with SPICE daemon")
    
    parser.add_argument("file", type=lambda x: yaml_interface.file_path(parser, x), help="LTSpice circuit to launch this script for.")
    
    args = parser.parse_args()
    
    filepath, filename, file_extension = args.file
    
    if platform != "linux":
        # wine doesn't like absolute paths, so just use the relative path spice_daemon/
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
                f.write("""sim:
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
    
    if args.generate == False and args.daemon == False and args.setup == False:
        args.generate, args.daemon = True, True
    
    if args.generate:
        
        source_data = yaml_interface.load_yaml(DAEMON_DEF_FILE)
        
        lib_content = "** Auto-generated by spice_daemon **\n\n"
        
        STEPS = source_data["sim"]["STEPS"]
        T = source_data["sim"]["T"]
        
        t = np.linspace(0, T, STEPS)
        
        print("Generating new components...")
        
        for key in source_data.keys():
            
            if key != "sim":
                
                generator = eval(key + "()")
        
                for source in source_data[key].keys():
                    
                    generator.load_data(source, source_data["noise_sources"][source])
                
                    lib_content += generator.lib_generator(DAEMON_FILE_DEST_PREAMBLE)
                    
                    yaml_interface.create_asy(filepath, LIB_FILE, source, element=generator, type=source_data["noise_sources"][source]["source_type"])
                    
                    generator.update_PWL_file(DAEMON_FILE_DEST_PREAMBLE, t)
            
                yaml_interface.write_lib(LIB_FILE, lib_content)

    if args.daemon:
        
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
        yaml_sources_time = os.path.getmtime(DAEMON_DEF_FILE)
        
        print("Launched noise daemon... Use LTSpice normally now :)")
        
        while True:
            
            time.sleep(1)
        
            source_data = yaml_interface.load_yaml(DAEMON_DEF_FILE)
            
            STEPS = source_data["sim"]["STEPS"]
            T = source_data["sim"]["T"]
            
            t = np.linspace(0, T, STEPS)
            
            try:
                
                spec_file_change = os.path.getmtime(DAEMON_DEF_FILE) > yaml_sources_time
            
                if os.path.getmtime(filepath + filename + ".log") > seed_time or spec_file_change:
                    
                    seed_time = os.path.getmtime(filepath + filename + ".log")
                    if spec_file_change: yaml_sources_time = os.path.getmtime(DAEMON_DEF_FILE)
                    
                    update_components(source_data, DAEMON_FILE_DEST_PREAMBLE, t)
                    
            except FileNotFoundError as e:
                
                if seed_time != None:
                    print("LTSpice closed, killing daemon")
                
                break