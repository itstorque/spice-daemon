Version 4
SymbolType BLOCK
LINE Normal -32 -4 -32 4
LINE Normal 36 -24 36 24
LINE Normal 36 0 48 0
LINE Normal -48 0 -32 0
ARC Normal -132 4 48 88 36 0 -36 -8
ARC Normal -132 -88 48 -4 -36 8 36 0
TEXT -32 -16 VLeft 0 Zlow=50
TEXT 32 -36 VLeft 0 Zhigh=1000
SYMATTR Prefix X
SYMATTR Description <class 'type'> noise source
SYMATTR SpiceModel taper_1
SYMATTR ModelFile /Users/torque/programs/spice-daemon/.spice-daemon-data/pynoise.lib
PIN 48 0 NONE 8
PINATTR PinName in
PINATTR SpiceOrder 1
PIN -48 0 NONE 8
PINATTR PinName out
PINATTR SpiceOrder 2