#!/usr/bin/env python3
import traceback
import argparse
import os
import time
from sys import platform

import numpy as np

from helpers import yaml_interface
from helpers.open_ltspice_file import *
from helpers.file_interface import File
from modules import *
from toolkit import *

DAEMON_MAIN_DIR = ".spice-daemon-data"
daemon_filename = "spice-daemon.yaml"

DAEMON_FILE_DEST_PREAMBLE = DAEMON_MAIN_DIR + "/noise_data_"
DAEMON_DEF_FILE = DAEMON_MAIN_DIR + "/" + daemon_filename
LIB_FILE = DAEMON_MAIN_DIR + "/spice-daemon.lib" 
DAEMON_TRAN_FILE = DAEMON_MAIN_DIR + "/trancmd.txt"

def write_tran_cmd(data, dir):
    
    body = ""
    
    data["Tstop"] = data["T"]
    data["STEPSIZE"] = data["T"]/data["STEPS"]
    
    for key in data.keys():
        body += ".param " + key + " " + str(data[key]) + "\n"
        
    body += """
    .options reltol 1e-6
    """
        
    with open(dir, 'w') as f:
        f.write(body)

def get_encoding_function(filedata):
    
    if 'Version'.encode('utf_16_le') in filedata[:20]:
        double_size = True
    elif 'Version'.encode('utf_8') in filedata[:20]:
        double_size = False
    else:
        raise Exception("Error reading asc file")
    
    def encode(bytes): 
        
        if double_size:
            
            encoded = b''
            
            for i in range(0, len(bytes)):
                k = bytearray(b'\x000')
                k[1] = bytes[i]
                encoded += k
                
            return encoded[1:]
        
        else:
            
            return bytes
        
    return encode

def check_for_daemon_setup(file):
    
    with open(file, 'rb') as f:
        filedata = f.read()
        
    encode = get_encoding_function(filedata)
    
    if encode(b";spice-daemon") in filedata:
        return True
    
    return False
            
def setup_tran_statement(file):
    
    filedata = None
    
    with open(file, 'rb') as f:
        filedata = f.read()
        
    encode = get_encoding_function(filedata)
    
    # # tran statement replace
    filedata = filedata.replace(encode(b"!.tran"), encode(b"; disabled by spice-daemon ;.tran"))
    # filedata += encode("\nTEXT 240 672 Left 2 !.include .spice-daemon-data/trancmd.txt")
    # filedata += encode("\nTEXT 392 544 Left 2 ;spice-daemon")
    # filedata += encode("\nRECTANGLE Normal 740 736 196 512 2")
    # filedata += encode("\nTEXT 240 624 Left 2 !.tran 0 {Tstop} 0 {STEPSIZE}")
    
    # The filedata below contains this byte string:
    # b'TEXT 240 672 Left 2 !.include .spice-daemon-data/trancmd.txt\nTEXT 392 544 Left 2 ;spice-daemon\nTEXT 240 624 Left 2 !.tran 0 {Tstop} 0 {STEPSIZE}\nRECTANGLE Normal 740 736 196 512 2\n'
    filedata += encode(bytes(
        [84, 69, 88, 84, 32, 50, 52, 48, 32, 54, 55, 50, 32, 76, 101, 102, 
         116, 32, 50, 32, 33, 46, 105, 110, 99, 108, 117, 100, 101, 32, 46, 
         115, 112, 105, 99, 101, 45, 100, 97, 101, 109, 111, 110, 45, 100, 
         97, 116, 97, 47, 116, 114, 97, 110, 99, 109, 100, 46, 116, 120, 116, 
         10, 84, 69, 88, 84, 32, 51, 57, 50, 32, 53, 52, 52, 32, 76, 101, 102, 
         116, 32, 50, 32, 59, 115, 112, 105, 99, 101, 45, 100, 97, 101, 109, 
         111, 110, 10, 84, 69, 88, 84, 32, 50, 52, 48, 32, 54, 50, 52, 32, 76, 
         101, 102, 116, 32, 50, 32, 33, 46, 116, 114, 97, 110, 32, 48, 32, 123, 
         84, 115, 116, 111, 112, 125, 32, 48, 32, 123, 83, 84, 69, 80, 83, 73, 
         90, 69, 125, 10, 82, 69, 67, 84, 65, 78, 71, 76, 69, 32, 78, 111, 114, 
         109, 97, 108, 32, 55, 52, 48, 32, 55, 51, 54, 32, 49, 57, 54, 32, 53, 
         49, 50, 32, 50, 10]))
    # encode(open('test/circuit copy.asc', 'rb').read())
    
    with open(file, 'wb') as f:
        f.write(filedata)

def update_components(source_data, daemon_file_dest_preamble, t, spec_changed=False, extensionless_file=None):
    
    lib_content = ""
    
    for key in source_data.keys():
            
        if key != "sim":
            
            generator = eval(key + "()")
            
            print(key)
            if key == "postprocessing":
                generator.path = extensionless_file
    
            for source in source_data[key].keys():
                
                if not spec_changed:
                    generator.load_data(source, source_data[key][source])
                    
                    generator.update_PWL_file(DAEMON_FILE_DEST_PREAMBLE, t)
                    
                else:
                
                    generator.load_data(source, source_data[key][source])
                
                    lib_content += generator.lib_generator(DAEMON_FILE_DEST_PREAMBLE)
                    
                    generator.update_PWL_file(DAEMON_FILE_DEST_PREAMBLE, t)
        
            if spec_changed: yaml_interface.write_lib(LIB_FILE, lib_content)

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
    
    asc_file = f"{filepath}{filename}.{file_extension}"
    
    if platform != "linux":
        # wine doesn't like absolute paths, so just use the relative path spice_daemon/
        DAEMON_FILE_DEST_PREAMBLE = filepath + DAEMON_FILE_DEST_PREAMBLE
        DAEMON_DEF_FILE   = filepath + DAEMON_DEF_FILE
        DAEMON_TRAN_FILE   = filepath + DAEMON_TRAN_FILE
        LIB_FILE          = filepath + LIB_FILE
    
    if args.setup:
        print("Setting up directory " + filepath)
        
        os.makedirs(DAEMON_MAIN_DIR, exist_ok=True)
        
        new_file_loc = DAEMON_DEF_FILE
        
        if check_for_daemon_setup(asc_file) == False:
            setup_tran_statement(asc_file)
        else:
            pass
            # TODO: figure out what to do when someoen tries to setup again.
        
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
        
    if check_for_daemon_setup(asc_file) == False:
        raise Exception("RUN SETUP COMMAND FIRST: \n \t \t spice -s " + asc_file)
    
    if args.generate:
        
        source_data = yaml_interface.load_yaml(DAEMON_DEF_FILE)
        
        print(source_data)
        
        lib_content = "** Auto-generated by spice_daemon **\n\n"
        
        STEPS = source_data["sim"]["STEPS"]
        T = source_data["sim"]["T"]
        
        write_tran_cmd(source_data['sim'], DAEMON_TRAN_FILE)
        
        t = np.linspace(0, T, STEPS)
        
        print("Generating new components...")
        
        for key in source_data.keys():
            
            if key != "sim":
                
                generator = eval(key + "()")
        
                for source in source_data[key].keys():
                    
                    generator.load_data(source, source_data[key][source])
                
                    lib_content += generator.lib_generator(DAEMON_FILE_DEST_PREAMBLE)
                    
                    yaml_interface.create_asy(filepath, LIB_FILE, source, element=generator)
                    
                    generator.update_PWL_file(DAEMON_FILE_DEST_PREAMBLE, t)
            
                yaml_interface.write_lib(LIB_FILE, lib_content)

    log_file = File(filepath + filename + ".log", force_run_spice_if_fail=f"{filepath}{filename}.{file_extension}")
    def_file = File(DAEMON_DEF_FILE)

    if args.daemon:
        
        # import time, os.path
        
        # try:
        #     seed_time = os.path.getmtime(filepath + filename + ".log")
            
        # except FileNotFoundError as e:
            
        #     if platform == "darwin":
        #         os.system(f"/Applications/LTspice.app/Contents/MacOS/LTspice -b {filepath}{filename}.{file_extension} & open " + f"{filepath}{filename}.{file_extension}")
                
        #     else:
                
        #         print("Could not find log file.")
        #         print("Make sure that the supplied file exists and make sure it is launched.")
                
        #         raise FileNotFoundError
            
        # seed_time = os.path.getmtime(filepath + filename + ".log")
        # yaml_sources_time = os.path.getmtime(DAEMON_DEF_FILE)
        
        print("Launched noise daemon... Use LTSpice normally now :)")
        
        while True:
            
            try:
            
                time.sleep(1)
            
                source_data = def_file.load_yaml() #yaml_interface.load_yaml(DAEMON_DEF_FILE)
                
                STEPS = source_data["sim"]["STEPS"]
                T = source_data["sim"]["T"]
                
                write_tran_cmd(source_data['sim'], DAEMON_TRAN_FILE)
                
                t = np.linspace(0, T, STEPS)
                
                try:
                
                    if log_file.did_change():
                        
                        update_components(source_data, DAEMON_FILE_DEST_PREAMBLE, t, spec_changed=def_file.did_content_change(), extensionless_file=filepath+filename)
                        
                    elif def_file.did_content_change():
                        
                        update_components(source_data, DAEMON_FILE_DEST_PREAMBLE, t, spec_changed=False, extensionless_file=filepath+filename)
                        
                except FileNotFoundError as e:
                    
                    print("LTSpice closed, killing daemon")
                    
                    break
                
            except Exception as e:
                
                traceback.print_exc()
                
                print("SPICE DAEMON FAILED:") 
                print(e)