from threading import Thread
from time import sleep

class WatchDog():
    
    def __init__(self, files, callback, delay=1):
        self.files = set(files)
        self.callback = callback
        
        self.running = False
        
        self.delay = delay
        
    def is_running(self):
        return self.running
    
    def watch(self):
        
        if not self.running: 
            self.running = True
            
        thread = Thread(target=self._watch)
        thread.start()
        thread.join()
            
    def _watch(self):

        while self.running:
            
            files_changed = self.check_changes()
            
            if len(files_changed) > 0:
                
                self.callback(files_changed)
                
            sleep(self.delay)

    def check_changes(self):
        
        res = set()
        
        for file in self.files:
            
            if file.did_change():
                res.add(file)
        
        return res