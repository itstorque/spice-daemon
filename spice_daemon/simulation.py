from pathlib import Path

# from file_interface import File
import spice_daemon as sd

class Simulation():
    
    OPT_CODES = {"reltol", "abstol"} # TODO: finish this!!
    
    def __init__(self, circuit_path, T=0, STEPS=0, params={}, opt_params={"reltol": 1e-6}, daemon_folder_loc=None, watchdog_delay=1):
        
        self.T     = T
        self.STEPS = STEPS
        
        self.params     = params
        self.opt_params = opt_params
        
        self.watchdog_delay = watchdog_delay
        
        self.circuit_path = Path(circuit_path)
        self.circuit_loc = self.circuit_path.parent.resolve()
        self.circuit_name = self.circuit_path.stem
        
        self.circuit_file = sd.helpers.File(self.circuit_path)
        
        if daemon_folder_loc==None:
            daemon_folder_loc = self.circuit_loc
        
        self.daemon_files = Path(daemon_folder_loc) / ".spice-daemon-data"
        # create dir if not found, doesn't create parents...
        self.daemon_files.mkdir(exist_ok=True)
        
        self.tran_file = sd.helpers.File(self.daemon_files / "trancmd.txt", touch=True)
        
        self.modules = set()
        self.toolkits = set()
        
        # logfile generated by LTspice
        self.log_file = sd.helpers.File( self.circuit_loc / (self.circuit_name + ".log"), touch=True ) # force_run_spice_if_fail was used before refactoring...
        
        try:
            # yaml definitions file
            self.def_file = sd.helpers.File( self.daemon_files / "spice-daemon.yaml" )
        except:
            self.create_yaml_file()
        
        # WatchDog watches files in self.watch_files for changes and runs a function whenever they are modified
        self.watch_files = {self.log_file, self.def_file}
        self.watchdog = None
        
    def update_tran_file(self):
        # Generates a tran file "trancmd.txt" in daemon_loc
        
        contents = f"""** GENERATED BY SPICE-DAEMON **\n
.param T {self.T}
.param STEPS {self.STEPS}
.param STEPSIZE {self.T/self.STEPS}\n\n"""

        for key, value in self.params.items():
            contents += f".param {key} {value}\n"

        for key, value in self.opt_params.items():
            contents += f".option {key} {value}\n"
        
        return self.tran_file.write(contents)
    
    def generate_modules(self):
        raise NotImplementedError
        
    def process_toolkits(self):
        raise NotImplementedError
    
    def add_module(self, module):
        
        if not isinstance(module, sd.helpers.Element):
            raise TypeError
        
        self.modules.add(module)
    
    def add_toolkit(self, toolkit):
        self.toolkits.add(toolkit)
        
    def clear_modules(self):
        self.modules = set()
        
    def clear_toolkits(self):
        self.toolkits = set()
        
    def add_module_from_def(self, module_type, params):
        
        for name in params:
        
            module = eval(f"sd.modules.{module_type}()")
            
            module.load_data(name, params[name])
            
            self.add_module(module)
            
            print(self.modules)
        
    def add_toolkit_from_def(self, name, params):
        
        # generator = eval(key + "()")
        pass
        
    def add_from_def_file(self):
        
        source_data = self.def_file.load_yaml()
        
        for type in source_data.keys():
            
            for entry in source_data[type].keys():
                
                value = source_data[type][entry]
            
                if type == "sim":
                    
                    # self.STEPS = source_data["sim"]["STEPS"]
                    # self.T = source_data["sim"]["T"]
                    
                    if entry == "STEPS":
                        self.STEPS = value
                        
                    elif entry == "T":
                        self.T = value
                        
                    elif entry in self.OPT_CODES:
                        self.opt_params[entry] = value
                        
                    else:
                        self.params[entry] = value
                    
                elif type in {"module", "modules"}:
                    
                    self.add_module_from_def(entry, value)
                    
                elif type in {"toolkit", "toolkits"}:

                    self.add_toolkit_from_def(entry, value)
                    
                else:
                    raise KeyError
        
    def on_update(self, changed):
        print("UPDATE", changed)
        
        if self.def_file in changed:
            # reimport modules and toolkits
            
            self.clear_modules()
            self.clear_toolkits()
            
            self.add_from_def_file()
        
    def run_watchdog(self):
        if self.watchdog and self.watchdog.is_running(): return
        
        self.watchdog = sd.helpers.WatchDog(self.watch_files, self.on_update, delay=self.watchdog_delay)
        
        self.watchdog.watch()
        
    def setup_tran_statement(self):
        
        data = self.circuit_file.read_bytes()
        
        data = data.replace(self.circuit_file.encode(b"!.tran"), self.circuit_file.encode(b"; disabled by spice-daemon ;.tran"))
        
        data += self.circuit_file.encode(bytes(
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
        
        self.circuit_file.write_bytes(data)
        
    # SETUP
    
    def create_yaml_file(self):
        
        default_yaml_file_content = """# THIS IS A SPICE-DAEMON YAML FILE\n
sim:
  T: 10e-9 # simulation end time
  STEPS: 100000 # number of simulation steps
  # Enter any other circuit parameters you want to use. e.g.
  L: 1 # you can put an inductor and set its inductance to \{L\} and it would be 1H
  
modules:
  # all the spice-daemon elements you want to add from spice-daemon into LTspice
  # they will be accessible from the LTspice components menu. 
  # Check under the components defined in your local directory not LTspice

  # To create two spice-daemon elements you can access in LTspice
  # put the type under modules (make sure to not have two separate noise_source entries)
  noise_sources:
  
    # create a noise_source called 'my_noise_source_1' with the following params
    my_noisy_source_1:
      source_type: voltage
      noise:
        type: gaussian
        mean: 0
        std: 2
       
    # create another noise source with a different name 
    another_noisy_source:
      source_type: current
      noise:
        type: gaussian
        mean: 0
        std: 2
      
toolkits:
  # toolkits are python side computations such as postprocessing data,
  # generating a matplotlib plot that accompanies your circuit or generating
  # tables for LTspice. Everything that isn't an LTspice component.
  
  PSD:
    out: "pcr_outa"
    trace: "I(R9)"
    gui: true"""
    
        self.def_file = sd.helpers.File( self.daemon_files / "spice-daemon.yaml", touch=True )
        
        self.def_file.write(default_yaml_file_content)