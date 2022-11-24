class WatchDog():
    
    def __init__(self, files, callback):
        self.files = set(files)
        self.callback = callback