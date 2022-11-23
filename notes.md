FFT output

Struggled to implement writing a `.fft` output for LTspice. This boils down to two parts, (1) the encoding seems to be different than `.out` and (2) It isn't obvious how to update the plot without closing the window and opening it up again in LTspice. A possible fix for (2) is hooking into LTspice methods but that would mean it is only supported as long as someone reverse engineers every version of LTspice and distributes it. This seems like too much work compared to just making a self-updating matplotlib plot that is much more customizable.

