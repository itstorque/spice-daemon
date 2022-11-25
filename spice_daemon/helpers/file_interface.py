import os
import hashlib
from sys import platform

import spice_daemon as sd

class File():
    
    def __init__(self, path, touch=False, force_run_spice_if_fail=False):
        # path is a Path object
        # Touch creates the file if it doesn't exist
        # force_run_spice_if_fail launches LTspice and opens the file
        
        self.path = path
        self.platform = platform
        self.force_run_spice_if_fail = force_run_spice_if_fail
        
        if touch:
            self.path.touch(exist_ok=True)
        
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
    
    def hash(self):

        h = hashlib.sha1()

        with open(self.path,'rb') as file:

            chunk = 0
            while chunk != b'':
                chunk = file.read(1024)
                h.update(chunk)
                
        return h.hexdigest()
    
    def encode(self, *args, **kwargs):
        # Used for LTspice circuits with weird encodings...
        # Caches the encoding while sd is running.
        
        # first call, runs get_encoding_function and uses that
        # after that encode is the encoded function
        self.encode = self.get_encoding_function()
        self.encode(*args, **kwargs)
    
    # Helpers for LTspice files
    def get_encoding_function(self):
        
        filedata = None
    
        with open(self.path, 'rb') as f:
            filedata = f.read()
    
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
    
    def read_bytes(self):
        # read raw bytes of file
    
        with open(self.path, 'rb') as f:
            return f.read()
    
    def write_bytes(self, data):
        
        with open(self.path, 'wb') as f:
            f.write(data)
    
    def write(self, data):
        
        with open(self.path, 'w+') as f:
            f.write(data)