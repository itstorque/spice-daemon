import spice_daemon.toolkit as sdt

class IVCurve(sdt.PostProcessorPlot):
    
    def __init__(self) -> None:
        super().__init__()
        
    def setup(self):
        super().setup()
        
        # TODO: create tran command update logic
        # self.append_tran_command()
        
    def post(self):
        super().post()
        
        return self.plot()