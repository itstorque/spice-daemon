#!/usr/bin/env python3

import os
import yaml
import re

'''
Functions for interacting with the yaml specification files
'''

class Element():
    '''
    Interface defining some necessary functions each 
    SPICE element needs to implement differently
    '''
    
    def generate_asy_content(self, filepath, filename, params):
        pass 

    def lib_generator(self, *args, **kwargs):
        pass
    
    def update_PWL_file(self, *args, **kwargs):
        pass
    
    def load_data(self, name, data):
        print(">>>", name)
        self.name = name
        self.data = data

def write_yaml(noise_source_dict, dest):

    with open(dest, 'w') as file:
        yaml.dump(noise_source_dict, file)
        
def load_yaml(src):
    
    with open(src, 'r') as file:
        return yaml.load(file, Loader=yaml_loader)

def write_lib(LIB_FILE, content):
    
    with open(LIB_FILE, "w") as f:
        
        f.write(content)
        f.close()

def create_asy(filepath, LIB_FILE, name, element):
    
    content = element.generate_asy_content(LIB_FILE, name)
    
    with open(filepath + name+".asy", "w") as f:
        
        f.write(content)
        f.close()

def file_path(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return os.path.dirname(os.path.abspath(arg)) + "/", \
               ''.join(os.path.basename(arg).split(".")[:-1]),\
               os.path.basename(arg).split(".")[-1]

# CUSTOM YAML LOADER
# 
# by default, loader doesn't accept 1e5, need 1.e+5...
# This implies + and .

yaml_loader = yaml.SafeLoader
yaml_loader.add_implicit_resolver(
        u'tag:yaml.org,2002:float',
        re.compile(u'''^(?:
        [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$''', re.X),
        list(u'-+0123456789.'))