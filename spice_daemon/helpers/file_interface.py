import os
import hashlib
from sys import platform

import spice_daemon as sd

class File():
    
    def __init__(self, path, force_run_spice_if_fail=False):
        
        self.path = path
        self.platform = platform
        self.force_run_spice_if_fail = force_run_spice_if_fail
        
        self.last_change_time = self.check_force_run_spice()
        
        self.last_change_time = 0 if self.last_change_time == None else self.last_change_time
        
        self.last_hash = self.hash()
    
    def last_modified(self):
        
        return os.path.getmtime(self.path)
    
    def last_accessed(self):
        
        return os.path.getmtime(self.path)
    
    def did_change(self):
        
        temp = self.last_modified() > self.last_change_time
        
        self.last_change_time = self.last_modified()
        
        return temp
    
    def did_content_change(self):
        
        if self.last_hash != self.hash(): 
            self.last_hash = self.hash()
            return True
        
        return False
    
    def check_force_run_spice(self, tolerate=True):
        # return last mod time if working
        
        if self.force_run_spice_if_fail==False: return
        
        try:
            return os.path.getmtime(self.path)
            
        except FileNotFoundError as e:
            
            if self.platform == "darwin" and tolerate:
                os.system(f"/Applications/LTspice.app/Contents/MacOS/LTspice -b {self.force_run_spice_if_fail} & open " + self.force_run_spice_if_fail)
                self.check_force_run_spice(tolerate=False)
                
            else:
                
                print("Could not find log file.")
                print("Make sure that the supplied file exists and make sure it is launched.")
                
                raise FileNotFoundError
        
    def load_yaml(self):
        return sd.helpers.load_yaml(self.path)
    
    def write(self):
        raise NotImplementedError
    
    def hash(self):

        h = hashlib.sha1()

        with open(self.path,'rb') as file:

            chunk = 0
            while chunk != b'':
                chunk = file.read(1024)
                h.update(chunk)
                
        return h.hexdigest()