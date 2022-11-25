from threading import Thread
from time import sleep

class WatchDog():
    
    def __init__(self, files, callback):
        self.files = set(files)
        self.callback = callback
        
        self.running = False
        
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
            print("running")
            sleep(1)