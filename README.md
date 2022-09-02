# spice-daemon

## Installation

Clone repo

Install pip packages

Add to path so you can run it anywhere using: `sudo ln -s $PWD/spice.py /usr/local/bin/spice`

#### Pip packages

- numpy
- colorednoise
- pyyaml
- scipy

TODOs: 
- integrate spice-noise-daemon git submodule properly...
- Johnson noise in noisy_resistor
- check blog...
- only update on change for non-entropic things
- default values
- should we migrate to deparable variables? I.e. generate gaussian dist w/o mu + sigma then feed those through the LTSpice UI? This also affects johnson noise, etc. What is the vision for this?