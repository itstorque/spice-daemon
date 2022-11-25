import numpy as np
import csv
import matplotlib.pyplot as plt
from math import isclose

'''
Helper functions for computing impedance matching taper coordinates
in Python. Works for any taper geometry for which width as a function
of length has been calculated.

function for taking taper widths --> gds coordinates based on Di Zhu 
and Marco Colangelo's generate_optimal_taper.m code

implemented in Python by Emma Batson
'''

def read_sonnet_csv(filename):
    ''' 
    filename: path to Sonnet CSV file

    read out some y value as a function of width
    from Sonnet output CSV with rows of form:
    0 - filepath DE_EMBEDDED w=val g=val
    1 - FREQUENCY (GHz) MAG[y]
    2 - freq, y

    returns: list[widths], list[ys]
    '''
    widths = []
    gs = []
    ys = []
    with open(filename) as csvfile:
        read = csv.reader(csvfile)
        for i, row in enumerate(read):
            # read width from 0th row
            if i % 3 == 0:
                startindex = row[0].find('w=')
                stopindex = row[0][startindex:].find('g=')
                width = float(row[0][startindex+2:startindex+stopindex-1])
                widths.append(width)
                g = float(row[0][startindex+stopindex+2:-1])
                gs.append(g)
            # read y value from 2nd row
            elif i % 3 == 2:
                ys.append(float(row[1]))
    return widths, ys, gs

def slice_by_gap(widths, gs, Zs, eEffs, gap_val):
    '''
    used for slicing a multidimensional dataset
    to take only widths and ys at a given gap value

    widths = arraylike of width values
    gs = arraylike of gap values, in same order
    Zs = arraylike of Z vals in same order
    eEffs = arraylike of eEffs in same order
    gap_val = desired gap value

    returns widths and ys at gap value
    '''
    gaps = np.array(gs)
    indices = np.where(gaps == gap_val)[0]
    new_widths = []
    new_Zs = []
    new_eEffs = []
    for i in indices:
        new_widths.append(widths[i])
        new_Zs.append(Zs[i])
        new_eEffs.append(eEffs[i])

    # sort based on widths
    zipped = zip(new_widths, new_Zs, new_eEffs)
    sorted_lists = sorted(zipped)
    tuples = zip(*sorted_lists)

    return [list(t) for t in tuples]

def sonnet_plot(filename, xvar='w', ylabel='Z'):
    width, y, g = read_sonnet_csv(filename)
    if xvar == 'w':
        plt.plot(width, y)
        plt.xlabel('Width [um]')
    elif xvar == 'g':
        plt.plot(g, y)
        plt.xlabel('Gap [um]')
    plt.ylabel(ylabel)
    plt.show()

class Coords:
    '''class for storing and manipulating gds coordinate values
    '''
    def __init__(self):
        ''' 
        w0 = initial width [um]
        gap = gap [um]
        initialize lists of coordinates as arrays with the same
        length as ls filled with zeros and create helper containers

        x0: center of trace
        x1: outermost (top) edge of taper
        x2: inner (top) edge of gap
        x3: inner (bottom) edge of gap
        x4: outermost (bottom) edge of taper
        '''
        # set up coordinate tracking indices
        self.x0 = []
        self.x1 = []
        self.x2 = []
        self.x3 = []
        self.x4 = []

        self.xlist = [self.x0, self.x1, self.x2, self.x3, self.x4]

        self.y0 = []
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.y4 = []

        self.ylist = [self.y0, self.y1, self.y2, self.y3, self.y4]

        self.all_coords = {'x': self.xlist, 'y': self.ylist}

    def initialize_taper(self, w, gap):
        for x in self.xlist:
            x.append(0)

        self.y0.append(0)
        self.set_ys(0, w, gap)

    def straight_xs(self, i, dl):
        ''' i: current index
        dl: change in absolute length between x[i-1], x[i] [um]

        populates all x-coords at i with x[i-1] + dl
        '''
        for xi in self.xlist:
            xi.append(self.x0[i-1] + dl)

    def set_ys(self, i, w, gap):
        '''i: current index
        w: width of wire [um]
        gap: width of gap [um]

        populates all y-coords at i with appropriate values
        relative to y0[i-1]
        '''
        self.y1.append(self.y0[i] + w/2 + gap) 
        self.y2.append(self.y0[i] + w/2)
        self.y3.append(self.y0[i] - w/2)
        self.y4.append(self.y0[i] - (w/2 + gap))

    def repeat_y0(self, i):
        '''i: current index

        populates y0[i] with same value as y0[i-1]
        '''
        self.y0.append(self.y0[i-1])

    def turn(self, axis, r0, w, gap, arc, origin):
        '''axis: x or y
        r0: radius of turn [um]
        w: width of wire [um]
        gap: width of gap [um]
        arc: trig(angle)
        origin: location of center of circle to draw

        populates all x or y at i with coordinates for turn
        '''
        coord_list = self.all_coords[axis]

        coord_list[0].append(origin + r0*arc)
        coord_list[1].append(origin + (r0 + w/2 + gap)*arc) 
        coord_list[2].append(origin + (r0 + w/2)*arc) 
        coord_list[3].append(origin + (r0 - w/2)*arc) 
        coord_list[4].append(origin + (r0 - (w/2 + gap))*arc)

    def add_top_pigtail(self, pigtail_coords):
        for xi, pigtail_xi in zip(self.xlist, pigtail_coords.xlist):
            xi[0:0] = pigtail_xi[:-2]

        for yi, pigtail_yi in zip(self.ylist, pigtail_coords.ylist):
            yi[0:0] = pigtail_yi[:-2]

    def add_bottom_pigtail(self, pigtail_coords, sgn):
        # I don't know why, but if there's an even number of rows,
        # the 2nd and 3rd coordinates get swapped
        if sgn == -1:
            self.x0.extend(pigtail_coords.x0)
            self.x1.extend(pigtail_coords.x1)
            self.x2.extend(pigtail_coords.x3)
            self.x3.extend(pigtail_coords.x2)
            self.x4.extend(pigtail_coords.x4)

            self.y0.extend(pigtail_coords.y0)
            self.y1.extend(pigtail_coords.y1)
            self.y2.extend(pigtail_coords.y3)
            self.y3.extend(pigtail_coords.y2)
            self.y4.extend(pigtail_coords.y4)
        else:
            for (xi, pigtail_xi) in zip(self.xlist, pigtail_coords.xlist):
                xi.extend(pigtail_xi)
            
            for yi, pigtail_yi in zip(self.ylist, pigtail_coords.ylist):
                yi.extend(pigtail_yi)

def generate_coords(ls, w_design, w_l, n_w, gap, dlmd0_um, brf=3, lmax=2500, M=360):
    ''' ls: array indicating physical distance [um] between normalized x coords
        w_design: w value [um] corresponding to each l value
        w_l: interpolation function giving w(l) [um -> um]
        n_w: interpolation function givin n(w) [um -> unitless]
        gap: width of gap [um]
        dlmd0_um: length per section [um]
        brf: bending radius factor
        lmax: maximum length of each turn [um]
        M: # pts while turning

        returns taper coordinates
        x0: center of trace
        x1: outermost (top) edge of taper
        x2: inner (top) edge of gap
        x3: inner (bottom) edge of gap
        x4: outermost (bottom) edge of taper
    '''
    coords = Coords()
    coords.initialize_taper(w_design[0], gap)

    print('start generating gds coords')

    # tracking variables
    row = 1
    flag_finish_before_turn = 0
    i = 1
    ltrack = 0

    # go to the second-to-last l value
    while ltrack < max(ls):
        w = w_l(ltrack)

        '''compute r0, radius of curvature to width [um]
        '''
        if w + 2*gap < 25:
            r0 = brf*(w + 2*gap)
        # reduce curvature radius for wide wires
        else:
            if row % 2 == 1:
                factor = 3
            else:
                factor = 1.5
            r0 = factor*(w + 2*gap)
            if r0 < brf*25:
                r0 = brf*25
        if row % 2 == 1:
            ''' if on an odd row, go right or turn clockwise
            choose direction to move
            '''
            if coords.x0[i-1] + r0 < lmax/2:
                # straight, to the right
                dl = dlmd0_um/n_w(w)
                coords.straight_xs(i, dl)
                coords.repeat_y0(i)
                coords.set_ys(i, w, gap)

                i+= 1
                ltrack += dl
            
            else:
                # start to turn, clockwise)
                theta = np.arange(0, np.pi, np.pi/M)

                xorigin = coords.x0[i-1]
                yorigin = coords.y0[i-1] - r0

                for elt in theta[1:]:
                    if ltrack >= max(ls):
                        w = w_design[-2]
                    else:
                        w = w_l(ltrack)

                    coords.turn('x', r0, w, gap, np.sin(elt), xorigin)
                    coords.turn('y', r0, w, gap, np.cos(elt), yorigin)

                    i+= 1
                    ltrack += r0*np.pi/M 

                    if ltrack > max(ls):
                        # keep turning until finished, even if length exceeded, but warn
                        flag_finish_before_turn = 1

                if flag_finish_before_turn:
                    print('finished while turning')
                # increase row index since we have turned onto the next one    
                row += 1
        elif row % 2 == 0:
            if coords.x0[i-1] - r0 > -lmax/2:
                # straight, to the left
                dl = dlmd0_um/n_w(w)
                coords.straight_xs(i, -dl)
                coords.repeat_y0(i)
                coords.set_ys(i, -w, -gap)

                i += 1
                ltrack += dl 

            else:
                # start to turn, counter-clockwise
                theta = np.arange(0, np.pi, np.pi/M)

                xorigin = coords.x0[i-1]
                yorigin = coords.y0[i-1] - r0

                for elt in theta:
                    if ltrack >= max(ls):
                        w = w_design[-2]
                    else:
                        w = w_l(ltrack)
                    
                    coords.turn('x', r0, -w, -gap, -np.sin(elt), xorigin)
                    coords.turn('y', r0, -w, -gap, np.cos(elt), yorigin)

                    i += 1
                    ltrack += r0*np.pi/M

                    if ltrack > max(ls):
                        # keep turning until finished, even if length exceeded, but warn
                        flag_finish_before_turn = 1
                if flag_finish_before_turn:
                    print('finished while turning')
                # increase row index since we have turned onto the next one    
                row += 1
    return coords, row

def generate_pigtail(coords, index, gap, M=360, brf=3, sgn=-1):
    '''
    coords: instance of Coords populated with taper by generate_coords
    index: location to add pigtails
    gap: gap between CPW and ground
    M: # of points while turning
    brf: bending radius factor

    returns coords for pigtail
    '''
    theta = np.arange(0, np.pi/2, np.pi/M)
    w = coords.y2[index] - coords.y3[index]
    r0 = brf*(w + 2*gap)

    xorigin = coords.x0[index]
    if index == 0:
        yorigin = coords.y0[index] + r0
    else:
        yorigin = coords.y0[index] - r0

    pigtail_coords = Coords()

    for elt in theta:
        if index == 0:
            pigtail_coords.turn('x', -r0, w, gap, np.cos(elt), xorigin)
            pigtail_coords.turn('y', -r0, w, gap, np.sin(elt), yorigin)
        else:
            pigtail_coords.turn('x', sgn*r0, w, gap, np.sin(elt), xorigin)
            pigtail_coords.turn('y', r0, sgn*w, gap, np.cos(elt), yorigin)

    return pigtail_coords

def generate_slope(coords, g_fxn, slope=0.1, Z=50, step=1, target_w=100, sgn = 1, analytical=False):
    '''
    coords: Coords class containing coordinates to add to
    g_fxn: function giving gap(w, Z) [um]
    slope: desired slope for w/y [um/um]
    Z: Z value to remain constant at [Ohms]
    step: step size for y [um]
    target_w: final width [um]
    '''
    w_init = coords.x2[-1] - coords.x3[-1]
    y_init = coords.y0[-1]
    x_origin = coords.x0[-1]
    
    w = w_init
    y = y_init

    while w < target_w:
        # step forward in y coord
        y -= step
        for yi in coords.ylist:
            yi.append(y)
        
        # linear increase to w
        w += slope*np.abs(y - y_init)
        # increase g to maintain constant Z
        if not analytical:
            g = g_fxn(np.stack([[w], [Z]], -1))[0]
        else:
            g = g_fxn(w)

        # add next step of x coords
        coords.x0.append(x_origin)
        coords.x1.append(x_origin + sgn*(0.5*w + g))
        coords.x2.append(x_origin + sgn*0.5*w)
        coords.x3.append(x_origin - sgn*0.5*w)
        coords.x4.append(x_origin - sgn*(0.5*w + g))
    return coords
