from __future__ import division, print_function, absolute_import
import numpy as np
from phidl import Device, Layer, make_device
import phidl.geometry as pg
import phidl.routing as pr
from phidl import quickplot as qp

from phidl import Device, Layer, LayerSet, make_device
from phidl import quickplot as qp # Rename "quickplot()" to the easier "qp()"
import phidl.geometry as pg
import phidl.routing as pr
import phidl.utilities as pu

import matplotlib.pyplot as plt


import scipy.io
import gdspy

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 12:13:36 2018

@author: Marco Colangelo
@author: Marco Colangelo

"""

"""
FUNCTION PARTS
"""

#%%  CPW componenets

def cpw_pad(width1=5, gap1=5, taper=True, length=1, width2 = 1, gap2 = 1,layer=1):
    D=Device('Pad')
    R1=pg.rectangle(size=(width1,width1))
    R1.add_port(name = 1, midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    R2=pg.outline(R1, distance = gap1, open_ports = 2*gap1+width1)
    r=D.add_ref(R2)
    if taper:
        T1=pg.taper(length, width1, width2)
        T1.rotate(90)
        T2=pg.taper(length, width1+2*gap1, width2+2*gap2)
        T2.rotate(90)
        TB=pg.boolean(T2, T1, 'A-B', 0.001)
        TB.add_port(name = 'wide', midpoint = T1.ports[1].midpoint, width = T1.ports[1].width, orientation = -90)
        TB.add_port(name = 'narrow', midpoint = T1.ports[2].midpoint, width = T1.ports[2].width, orientation = 90)
        t=D.add_ref(TB)
        r.move(r.ports[1],t.ports['wide'])
        D.flatten(single_layer = layer)
        D.add_port(name = 'out', midpoint = T1.ports[2].midpoint, width = T1.ports[2].width, orientation = 90)
    else:
        D.flatten(single_layer = layer)
        D.add_port(name = 'out', midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    return D    

def hyper_taper (length, wide_section, narrow_section, layer=1):
    """
    Hyperbolic taper (solid). Designed by colang.
    Parameters
    ----------
    length : FLOAT
        Length of taper.
    wide_section : FLOAT
        Wide width dimension.
    narrow_section : FLOAT
        Narrow width dimension.
    layer : INT, optional
        Layer for device to be created on. The default is 1.
    Returns
    -------
    HT :  DEVICE
        PHIDL device object is returned.
    """
    taper_length=length
    wide =  wide_section
    zero = 0
    narrow = narrow_section
    x_list = np.arange(0,taper_length+.1, .1)
    x_list2= np.arange(taper_length,-0.1,-0.1)
    pts = []
    a = np.arccosh(wide/narrow)/taper_length
    for x in x_list:
        pts.append((x, np.cosh(a*x)*narrow/2))
    for y in x_list2:
        pts.append((y, -np.cosh(a*y)*narrow/2))
        HT = Device('hyper_taper')
        hyper_taper = HT.add_polygon(pts, layer = 2)
        HT.add_port(name = 'narrow', midpoint = [0, 0],  width = narrow, orientation = 180)
        HT.add_port(name = 'wide', midpoint = [taper_length, 0],  width = wide, orientation = 0)
        HT.flatten(single_layer = layer)
    return HT

def cpw_taper(width1=5, gap1=5, taper=True, length=1, width2 = 1, gap2 = 1,layer=1):
    D=Device('Pad')
    T1=pg.taper(length, width1, width2)
    T1.rotate(90)
    T2=pg.taper(length, width1+2*gap1, width2+2*gap2)
    T2.rotate(90)
    TB=pg.boolean(T2, T1, 'A-B', 0.001)
    TB.add_port(name = 'wide', midpoint = T1.ports[1].midpoint, width = T1.ports[1].width, orientation = -90)
    TB.add_port(name = 'narrow', midpoint = T1.ports[2].midpoint, width = T1.ports[2].width, orientation = 90)
    t=D.add_ref(TB)
    D.flatten(single_layer = layer)
    D.add_port(name = 'out', midpoint = T1.ports[2].midpoint, width = T1.ports[2].width, orientation = 90)
    D.add_port(name = 'in', midpoint = T1.ports[1].midpoint, width = T1.ports[1].width, orientation = -90)
    return D  

def cpw_square_turn(width=5, gap=5,length=5, taper=True,layer=1):
    width1=width
    gap1=gap
    D=Device('Pad')
    R1=pg.rectangle(size=(length,width1))
    R1.add_port(name = 1, midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    R2=pg.outline(R1, distance = width1, open_ports = 2*gap1+length+width1)
    R3=pg.outline(R2, distance = gap1, open_ports = 2*gap1+width1+length)
    R3.flatten()
    r=D.add_ref(R3)
    D.flatten(single_layer = layer)
    D.add_port(name = 'out', midpoint = [R1.center[0]++width1/2+length/2,2*R1.center[1]], width = 2*R1.center[1]+1, orientation = 90)
    D.add_port(name = 'in', midpoint = [R1.center[0]-width1/2-length/2,2*R1.center[1]], width = 2*R1.center[1]+1, orientation = 90)
    return D    



def cpw_line(width=5, gap=5, length=10,layer=1):
    D=Device('Pad')
    R1=pg.rectangle(size=(width,length))
    R1.add_port(name = 'out', midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    R1.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    R2=pg.outline(R1, distance = gap, open_ports = 2*gap+width+100)
    r=D.add_ref(R2)
    D.flatten(layer)
    D.add_port(name = 'out', midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    D.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    return D


def cpw_turn(width=5, gap=5, length=10, radius=5, theta = 180, start_angle=0, layer=1):
    D=Device('Pad')
    A1=pg.arc(radius, width, theta, start_angle=start_angle, angle_resolution = 1, layer=layer)
    A2=pg.outline(A1, distance = gap, open_ports = 2*gap+width+100, layer=layer)
    D.add_ref(A2)
    D.flatten(layer)
    D.add_port(name = 'out', midpoint = [A2.ports[2].midpoint[0],A2.ports[2].midpoint[1]], width = A2.ports[2].width, orientation = A2.ports[2].orientation)
    D.add_port(name = 'in', midpoint = [A2.ports[1].midpoint[0],A2.ports[1].midpoint[1]], width = A2.ports[1].width, orientation = A2.ports[1].orientation)
    return D


    # R1=pg.rectangle(size=(width,length))
    # R1.add_port(name = 'out', midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    # R1.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    # R2=pg.outline(R1, distance = gap, open_ports = 2*gap+width)
    # r=D.add_ref(R2)
    # D.flatten(layer)
    # D.add_port(name = 'out', midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    # D.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    # return D


def cpw_short(width=5, gap=5, length=10,layer=1):
    D=Device('Pad')
    R1=pg.rectangle(size=(width,length))
    R1.add_port(name = 'out', midpoint = [R1.center[0],2*R1.center[1]], width = 2*R1.center[1], orientation = 90)
    R1.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    R2=pg.outline(R1, distance = gap, open_ports = 2*gap+width)
    r=D.add_ref(R2)
    D.flatten(layer)
    D.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    return D

def cpw_open(width=5, gap=5, length=10,layer=1):
    D=Device('Pad')
    R1=pg.rectangle(size=(width,length))
    R1.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    R2=pg.outline(R1, distance = gap, open_ports = 2*gap+width)
    r=D.add_ref(R2)
    D.flatten(layer)
    D.add_port(name = 'in', midpoint = [R1.center[0],0], width = 2*R1.center[1], orientation = -90)
    return D

def prepare_for_simulation(D,box_distance=10, w=10 ,g=10):
    C=Device('full')
    box = pg.bbox(bbox = D.bbox, layer = 1)
    BOXX = pg.offset(box,distance=box_distance)
    OUT=pg.boolean(BOXX,D,'A-B',precision=0.01,layer=2)
    out=C.add_ref(OUT)
    boxx2=pg.copy_layer(BOXX,0,1)
    boxx3=pg.copy_layer(BOXX,0,3)

    C.add_ref(boxx2)
    C.add_ref(boxx3)

   

    R1=pg.rectangle(size=(w,g))
    r1=C.add_ref(R1)
    r1.move(r1.center, (r1.center[0]-w/2,r1.center[1]-g-w))
    return C


#%% CPW same ratio straight not centered
def CPW_taper(coords, port1="narrow", port2="wide"):
    T = Device('taper')

    #plt.plot(x0, y0)
    x0 = np.reshape(coords.x0, (len(coords.x0), 1))
    y0 = np.reshape(coords.y0, (len(coords.x0), 1))

    #print(coords.x1)
    x1 = np.reshape(coords.x1, (len(coords.x0), 1))
    y1 = np.reshape(coords.y1, (len(coords.x0), 1))
    x2 = np.reshape(coords.x2, (len(coords.x0), 1))
    y2 = np.reshape(coords.y2, (len(coords.x0), 1))
    x3 = np.reshape(coords.x3, (len(coords.x0), 1))
    y3 = np.reshape(coords.y3, (len(coords.x0), 1))
    x4 = np.reshape(coords.x4, (len(coords.x0), 1))
    y4 = np.reshape(coords.y4, (len(coords.x0), 1))

#cut the structure every 100 points
    N = 100
    for i in range(1, len(x1)//N+1):
        x1_1 = x1[(i-1)*N:i*N+1]
        y1_1 = y1[(i-1)*N:i*N+1]
        x2_1 = x2[(i-1)*N:i*N+1]
        y2_1 = y2[(i-1)*N:i*N+1]    
        xlist12 = np.vstack((x1_1, x2_1[::-1]))
        ylist12 = np.vstack((y1_1, y2_1[::-1]))
        xylist12 = np.column_stack((xlist12, ylist12))
        T.add_polygon(xylist12,layer = 1)
        x3_1 = x3[(i-1)*N:i*N+1]
        y3_1 = y3[(i-1)*N:i*N+1]
        x4_1 = x4[(i-1)*N:i*N+1]
        y4_1 = y4[(i-1)*N:i*N+1]    
        xlist34 = np.vstack((x3_1, x4_1[::-1]))
        ylist34 = np.vstack((y3_1, y4_1[::-1]))
        xylist34 = np.column_stack((xlist34, ylist34))
        T.add_polygon(xylist34,layer = 1)

    x1_1 = x1[(len(x1)-1)//N*N:len(x1)+1]
    y1_1 = y1[(len(x1)-1)//N*N:len(x1)+1]
    x2_1 = x2[(len(x1)-1)//N*N:len(x1)+1]
    y2_1 = y2[(len(x1)-1)//N*N:len(x1)+1]
    x3_1 = x3[(len(x1)-1)//N*N:len(x1)+1]
    y3_1 = y3[(len(x1)-1)//N*N:len(x1)+1]
    x4_1 = x4[(len(x1)-1)//N*N:len(x1)+1]
    y4_1 = y4[(len(x1)-1)//N*N:len(x1)+1]
    xlist12 = np.vstack((x1_1, x2_1[::-1]))
    ylist12 = np.vstack((y1_1, y2_1[::-1]))
    xy12list = np.column_stack((xlist12, ylist12))
    T.add_polygon(xy12list, layer = 1)
    xlist34 = np.vstack((x3_1, x4_1[::-1]))
    ylist34 = np.vstack((y3_1, y4_1[::-1])) 
    xylist34 = np.column_stack((xlist34, ylist34))
    T.add_polygon(xylist34, layer = 1)

    T.add_port(name = port1, midpoint = [float(x0[0]),float(y0[0])], width = float(abs(x1[0]-x2[0])), orientation = 90)
    T.add_port(name = port2, midpoint = [float(x0[-1]),float(y0[-1])], width = float(abs(x1[-1]-x2[-1])), orientation = 270)
    return T
#%% MICROSTRIP TAPER
def microstrip_taper_st():
    T = Device('taper')
    mat = scipy.io.loadmat(r'C:\Users\Marco Colangelo\Dropbox (MIT)\5GHz-coupler\2019-09-25_taper_profile_2500MHz_gap=5um_w1=300nm_lmax=350um')
    x0 = mat['x0']
    y0 = mat['y0']
    x1 = mat['x1']
    y1 = mat['y1']
    x2 = mat['x2']
    y2 = mat['y2']
    x3 = mat['x3']
    y3 = mat['y3']
    x4 = mat['x4']
    y4 = mat['y4']
    
    #cut the structure every 100 points
    N = 200;
    for i in range(1, len(x1)//N+1):
        x2_1 = x2[(i-1)*N:i*N+1]
        y2_1 = y2[(i-1)*N:i*N+1]   
        x3_1 = x3[(i-1)*N:i*N+1]
        y3_1 = y3[(i-1)*N:i*N+1]
        xlist23 = np.vstack((x2_1, x3_1[::-1]))
        ylist23 = np.vstack((y2_1, y3_1[::-1]))
        xylist23 = np.column_stack((xlist23, ylist23))
        T.add_polygon(xylist23,layer = 1)
    x2_1 = x2[(len(x2)-1)//N*N:len(x2)+1]
    y2_1 = y2[(len(x2)-1)//N*N:len(x2)+1]
    x3_1 = x3[(len(x2)-1)//N*N:len(x2)+1]
    y3_1 = y3[(len(x2)-1)//N*N:len(x2)+1]
    xlist23 = np.vstack((x2_1, x3_1[::-1]))
    ylist23 = np.vstack((y2_1, y3_1[::-1]))
    xy23list = np.column_stack((xlist23, ylist23))
    T.add_polygon(xy23list, layer = 1)
    T.add_port(name = 'narrow', midpoint = [float(x0[0]),float(y0[0])], width = float(abs(y2[0]-y3[0])), orientation = 180)
    T.add_port(name ='wide', midpoint = [float(x0[-1]),float(y0[-1])], width = float(abs(y2[-1]-y3[-1])), orientation = 0)
    T.flatten(single_layer = 0)
    #T.write_gds('impedancematchedtaped.gds')
    return T




def microstrip_taper_c():
    T = Device('taper')
    mat = scipy.io.loadmat(r'G:\My Drive\qnn-lab\projects\sto_snspd\2021-01-26_taper_profile_500MHz_gap=1um_w1=100nm_lmax=7000um.mat')
    x0 = mat['x0']
    y0 = mat['y0']
    x1 = mat['x1']
    y1 = mat['y1']
    x2 = mat['x2']
    y2 = mat['y2']
    x3 = mat['x3']
    y3 = mat['y3']
    x4 = mat['x4']
    y4 = mat['y4']
    
    #cut the structure every 100 points
    N = 200;
    for i in range(1, len(x1)//N+1):
        x2_1 = x2[(i-1)*N:i*N+1]
        y2_1 = y2[(i-1)*N:i*N+1]   
        x3_1 = x3[(i-1)*N:i*N+1]
        y3_1 = y3[(i-1)*N:i*N+1]
        xlist23 = np.vstack((x2_1, x3_1[::-1]))
        ylist23 = np.vstack((y2_1, y3_1[::-1]))
        xylist23 = np.column_stack((xlist23, ylist23))
        T.add_polygon(xylist23,layer = 1)
    x2_1 = x2[(len(x2)-1)//N*N:len(x2)+1]
    y2_1 = y2[(len(x2)-1)//N*N:len(x2)+1]
    x3_1 = x3[(len(x2)-1)//N*N:len(x2)+1]
    y3_1 = y3[(len(x2)-1)//N*N:len(x2)+1]
    xlist23 = np.vstack((x2_1, x3_1[::-1]))
    ylist23 = np.vstack((y2_1, y3_1[::-1]))
    xy23list = np.column_stack((xlist23, ylist23))
    T.add_polygon(xy23list, layer = 1)
    T.add_port(name = 'narrow', midpoint = [float(x0[0]),float(y0[0])], width = float(abs(x2[0]-x3[0])), orientation = 90)
    T.add_port(name ='wide', midpoint = [float(x0[-1]),float(y0[-1])], width = float(abs(x2_1[-1]-x3_1[-1])), orientation = -90)
    T.flatten(single_layer = 0)
    #T.write_gds('impedancematchedtaped.gds')
    return T
#
#X=microstrip_taper()




#def cpw_trace_old(length, width, ratio, pnarrow, pwide, offset):
#    CPW= Device('CPW')
#    ang=np.degrees(np.arctan(offset/length))
#    length=length+width*np.tan(np.radians(ang))/2
#    narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
#    wide= CPW.add_port(name = 'wide', midpoint = [0,length],  width = pwide, orientation = -90)
#    cc=CPW.add_ref(pr.route_basic(narrow, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
#    gleft_pts=[[-width/2,0],[-width/2,length],[wide.midpoint[0]-wide.width/2-wide.width*ratio,length],[narrow.midpoint[0]-narrow.width/2-narrow.width*ratio,0]]
#    gleft=CPW.add_polygon(gleft_pts)
#    gright_pts=[[width/2,0],[width/2,length],[wide.midpoint[0]+wide.width/2+wide.width*ratio,length],[narrow.midpoint[0]+narrow.width/2+narrow.width*ratio,0]]
#    gright=CPW.add_polygon(gright_pts)
#    BOX=Device('BOX')
#    rect=BOX.add_ref(pg.rectangle(size=(width,length),layer=0))
#    rect.move(origin=rect.center, destination=(0,length/2))
#    trace=pg.boolean(rect,CPW,'A-B',0.00001,0)
#    X=Device('trace')
#    X.add_ref(trace)
#    narrow=X.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
#    pin=X.add_port(name = 'pin', midpoint = [narrow.midpoint[0]+narrow.width/2,0],  width =0.00000000000001, orientation = 90)
#    wide= X.add_port(name = 'wide', midpoint = [0,length],  width = pwide, orientation = -90)
#    X.rotate(angle=-ang, center=(narrow.midpoint[0],narrow.midpoint[1]))
##    X.rotate(angle=-ang, center=(pin.midpoint[0],pin.midpoint[1]))
#    return X
##
##X=cpw_trace(1000,1000,0.8,10,100,1000)
##qp(X)
#
#def cpw_off(length, width, ratio, pnarrow, pwide, offset):
#    CPW= Device('CPW')
#    ang=np.degrees(np.arctan(offset/length))
#    length=length+width*np.tan(np.radians(ang))/2
#    narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
#    wide= CPW.add_port(name = 'wide', midpoint = [0,length],  width = pwide, orientation = -90)
#    cc=CPW.add_ref(pr.route_basic(narrow, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
#    gleft_pts=[[-width/2,0],[-width/2,length],[wide.midpoint[0]-wide.width/2-wide.width*ratio,length],[narrow.midpoint[0]-narrow.width/2-narrow.width*ratio,0]]
#    gleft=CPW.add_polygon(gleft_pts)
#    gright_pts=[[width/2,0],[width/2,length],[wide.midpoint[0]+wide.width/2+wide.width*ratio,length],[narrow.midpoint[0]+narrow.width/2+narrow.width*ratio,0]]
#    gright=CPW.add_polygon(gright_pts)
#    CPW.rotate(angle=-ang, center=(narrow.midpoint[0],narrow.midpoint[1]))
#    return CPW
##X=cpw_off(1000,1000,0.8,10,100,1000)
##qp(X)
#
###%% CPW same ratio straight
#def cpw(length, width, ratio, pnarrow, pwide):
#    CPW= Device('CPW')
#    narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
#    wide= CPW.add_port(name = 'wide', midpoint = [0,length],  width = pwide, orientation = -90)
#    cc=CPW.add_ref(pr.route_basic(narrow, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
#    gleft_pts=[[-width/2,0],[-width/2,length],[wide.midpoint[0]-wide.width/2-wide.width*ratio,length],[narrow.midpoint[0]-narrow.width/2-narrow.width*ratio,0]]
#    gleft=CPW.add_polygon(gleft_pts)
#    gright_pts=[[width/2,0],[width/2,length],[wide.midpoint[0]+wide.width/2+wide.width*ratio,length],[narrow.midpoint[0]+narrow.width/2+narrow.width*ratio,0]]
#    gright=CPW.add_polygon(gright_pts)
#    return CPW





#%% COUPLER SECTIONSQ
def coupler_section_sq(c_length, c_distance, width, radius):
    ARM= Device('arm')

    begin=ARM.add_port(name = 'begin', midpoint = [0,0],  width = width, orientation = 90)

    #TURN1=pg.turn(begin, radius = radius, angle = 90, angle_resolution = 2, layer = 0)
    #turn1=ARM.add_ref(TURN1)

    TURN2=pg.turn(begin, radius = radius, angle = -45, angle_resolution = 2, layer = 0)
    turn2=ARM.add_ref(TURN2)

    STRAIGHT=pg.straight(size = (width,c_length), layer = 0)
    STRAIGHT.rotate(angle = 135, center = STRAIGHT.ports[1].midpoint)
    STRAIGHT.move(origin = STRAIGHT.ports[1], destination = turn2.ports[2])
    straight=ARM.add_ref(STRAIGHT)

    TURN3=pg.turn(straight.ports[2],  radius = radius, angle = -45, angle_resolution = 2, layer = 0)
    turn3=ARM.add_ref(TURN3)

    #TURN4=pg.turn(turn3.ports[2],  radius = radius, angle = -90, angle_resolution = 2, layer = 0)
    #turn4=ARM.add_ref(TURN4)

    #arm_in=ARM.add_port(name = 1, midpoint = turn1.ports[2].midpoint,  width = width, orientation = 180)
    end=ARM.add_port(name ='two', midpoint = turn3.ports[2].midpoint,  width = width, orientation = 0)
    begin=ARM.add_port(name ='one', midpoint = turn2.ports[1].midpoint,  width = width, orientation = -90)
    ARM.rotate(-45)
    coordinate = straight.ports[1].midpoint
    C= Device('trans')
    

    arm1=C.add_ref(ARM)
    arm2=C.add_ref(ARM)
    arm2.reflect((0,coordinate[1]+width/2+c_distance/2),(1,coordinate[1]+width/2+c_distance/2))
    C.add_port(port=arm2.ports['one'], name='one' )
    C.add_port(port=arm2.ports['two'], name='two')
    C.add_port(port=arm1.ports['one'], name='four')
    C.add_port(port=arm1.ports['two'], name='three')

    return C



#%% COUPLER SECTION
def coupler_section(c_length, c_distance, width, radius):
    ARM= Device('arm')

    begin=ARM.add_port(name = 'begin', midpoint = [0,0],  width = width, orientation = 90)

    #TURN1=pg.turn(begin, radius = radius, angle = 90, angle_resolution = 2, layer = 0)
    #turn1=ARM.add_ref(TURN1)

    TURN2=pg.turn(begin, radius = radius, angle = -90, angle_resolution = 2, layer = 0)
    turn2=ARM.add_ref(TURN2)

    STRAIGHT=pg.straight(size = (width,c_length), layer = 0)
    STRAIGHT.rotate(angle = 90, center = STRAIGHT.ports[1].midpoint)
    STRAIGHT.move(origin = STRAIGHT.ports[1], destination = turn2.ports[2])
    straight=ARM.add_ref(STRAIGHT)

    TURN3=pg.turn(straight.ports[2],  radius = radius, angle = -90, angle_resolution = 2, layer = 0)
    turn3=ARM.add_ref(TURN3)

    #TURN4=pg.turn(turn3.ports[2],  radius = radius, angle = -90, angle_resolution = 2, layer = 0)
    #turn4=ARM.add_ref(TURN4)

    #arm_in=ARM.add_port(name = 1, midpoint = turn1.ports[2].midpoint,  width = width, orientation = 180)
    end=ARM.add_port(name ='two', midpoint = turn3.ports[2].midpoint,  width = width, orientation = -90)
    begin=ARM.add_port(name ='one', midpoint = turn2.ports[1].midpoint,  width = width, orientation = -90)
    coordinate = straight.ports[1].midpoint
    C= Device('trans')

    arm1=C.add_ref(ARM)

    arm2=C.add_ref(ARM)
    arm2.reflect((0,coordinate[1]+width/2+c_distance/2),(1,coordinate[1]+width/2+c_distance/2))
    C.add_port(port=arm2.ports['one'], name='one' )
    C.add_port(port=arm2.ports['two'], name='two')
    C.add_port(port=arm1.ports['one'], name='four')
    C.add_port(port=arm1.ports['two'], name='three')
    return C






#%% MICROSTRIP TAPER
def microstrip_taper():
    T = Device('taper')
    mat = scipy.io.loadmat(r'G:\My Drive\qnn-lab\projects\sto_snspd\2021-01-27_taper_profile_500MHz_gap=1um_w1=300nm_lmax=7000um.mat')
    x0 = mat['x0']
    y0 = mat['y0']
    x1 = mat['x1']
    y1 = mat['y1']
    x2 = mat['x2']
    y2 = mat['y2']
    x3 = mat['x3']
    y3 = mat['y3']
    x4 = mat['x4']
    y4 = mat['y4']
    
    #cut the structure every 100 points
    N = 200;
    for i in range(1, len(x1)//N+1):
        x2_1 = x2[(i-1)*N:i*N+1]
        y2_1 = y2[(i-1)*N:i*N+1]   
        x3_1 = x3[(i-1)*N:i*N+1]
        y3_1 = y3[(i-1)*N:i*N+1]
        xlist23 = np.vstack((x2_1, x3_1[::-1]))
        ylist23 = np.vstack((y2_1, y3_1[::-1]))
        xylist23 = np.column_stack((xlist23, ylist23))
        T.add_polygon(xylist23,layer = 1)
    x2_1 = x2[(len(x2)-1)//N*N:len(x2)+1]
    y2_1 = y2[(len(x2)-1)//N*N:len(x2)+1]
    x3_1 = x3[(len(x2)-1)//N*N:len(x2)+1]
    y3_1 = y3[(len(x2)-1)//N*N:len(x2)+1]
    xlist23 = np.vstack((x2_1, x3_1[::-1]))
    ylist23 = np.vstack((y2_1, y3_1[::-1]))
    xy23list = np.column_stack((xlist23, ylist23))
    T.add_polygon(xy23list, layer = 1)
    T.add_port(name = 'narrow', midpoint = [float(x0[0]),float(y0[0])], width = float(abs(x2[0]-x3[0])), orientation = 90)
    T.add_port(name ='wide', midpoint = [float(x0[-1]),float(y0[-1])], width = float(abs(x2[-1]-x3[-1])), orientation = 270)
    T.flatten(single_layer = 0)
    #T.write_gds('impedancematchedtaped.gds')
    qp(T)
    return T
#
#X=microstrip_taper()



#%% HYPER TAPER 
def hyper_taper (length, wide_section, narrow_section, layer=1):
    taper_length=length
    wide =  wide_section
    zero = 0
    narrow = narrow_section
    x_list = np.arange(0,taper_length+.1, .1)
    x_list2= np.arange(taper_length,-0.1,-0.1)
    pts = []

    a = np.arccosh(wide/narrow)/taper_length

    for x in x_list:
        pts.append((x, np.cosh(a*x)*narrow/2))
    for y in x_list2:
        pts.append((y, -np.cosh(a*y)*narrow/2))
        HT = Device('hyper_taper')
        hyper_taper = HT.add_polygon(pts, layer = 2)
        HT.add_port(name = 'narrow', midpoint = [0, 0],  width = narrow, orientation = 180)
        HT.add_port(name = 'wide', midpoint = [taper_length, 0],  width = wide, orientation = 0)
        HT.flatten(single_layer = layer)
    return HT

#%% optimal 90 deg
def optimal_90deg(width = 100.0, num_pts = 15, length_adjust = 1, layer = 0):
    D = Device()

    # Get points of ideal curve
    a = 2*width
    v = np.logspace(-length_adjust,length_adjust,num_pts)
    xi = a/2.0*((1+2/np.pi*np.arcsinh(1/v)) + 1j*(1+2/np.pi*np.arcsinh(v)))
    xpts = list(np.real(xi)); ypts = list(np.imag(xi))
    
    # Add points for the rest of curve
    d = 2*xpts[0] # Farthest point out * 2, rounded to nearest 100
    xpts.append(width); ypts.append(d)
    xpts.append(0); ypts.append(d)
    xpts.append(0); ypts.append(0)
    xpts.append(d); ypts.append(0)
    xpts.append(d); ypts.append(width)
    xpts.append(xpts[0]); ypts.append(ypts[0])
    
    D.add_polygon([xpts, ypts], layer = layer)
    
    D.add_port(name = 1, midpoint = [a/4,d], width = a/2, orientation = 90)
    D.add_port(name = 2, midpoint = [d,a/4], width = a/2, orientation = 0)
    return D
#%% Meandered w/ NW section
    
def meandered_nw_sec (straights, turns, left, ratio_radius, width, meander_length, section_length, section_width):
    left=left;
    s=straights
    t=turns;
    total_steps=s+t;
    c=3e9;
    meander_length=meander_length;
    width=width;
    ratio_radius=ratio_radius;
    D= Device('meandered_NW')
    begin=D.add_port(name = 'begin', midpoint = [0,0],  width = width, orientation = 0)

    STRAIGHT=pg.straight(size = (width,left/2), layer = 0)
    STRAIGHT.rotate(-90)
    STRAIGHT.move(origin = STRAIGHT.ports[2], destination = begin)
    straight=D.add_ref(STRAIGHT)
    
    TURN=pg.turn(straight.ports[1], radius = 3*width, angle = 90, angle_resolution = 2, layer = 0)
    turn=D.add_ref(TURN)
#    qp(D)

    STRAIGHT=pg.straight(size = (width,meander_length/2), layer = 0)
    STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
    straight=D.add_ref(STRAIGHT)
    TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
    turn=D.add_ref(TURN)
    coordinate=turn.ports[2]
#    qp(D)

    while s > 0 and t > -1:
        if s==int(straights/2):
             STRAIGHT=pg.straight(size = (width,(meander_length-section_length*2)/2), layer = 0)
             STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
             straight=D.add_ref(STRAIGHT)
             ht1=D.add_ref(hyper_taper(section_length/2, width, section_width))
             ht1.rotate(90)
             ht1.move(ht1.ports['wide'], straight.ports[2])
             STRAIGHT=pg.straight(size = (section_width,section_length), layer = 0)
             STRAIGHT.move(origin = STRAIGHT.ports[1], destination = ht1.ports['narrow'])
             straight=D.add_ref(STRAIGHT)
             ht2=D.add_ref(hyper_taper(section_length/2, width, section_width))
             ht2.rotate(-90)
             ht2.move(ht2.ports['narrow'], straight.ports[2])
             STRAIGHT=pg.straight(size = (width,(meander_length-section_length*2)/2), layer = 0)
             STRAIGHT.move(origin = STRAIGHT.ports[1], destination = ht2.ports['wide'])
             straight=D.add_ref(STRAIGHT)
             s=s-1;
        else:
            #        if divmod(x,2)[1] == 0:
            STRAIGHT=pg.straight(size = (width,meander_length), layer = 0)
            STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
            straight=D.add_ref(STRAIGHT)
            s=s-1;
        if s==0 and t==0 :
            break
        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        t=t-1;
        coordinate=turn.ports[2]
        if s==0 and t==0 :
            break
        STRAIGHT=pg.straight(size = (width,meander_length), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        s=s-1;
        if s==0 and t==0 :
            break
        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        t=t-1;
        coordinate=turn.ports[2]
        
    if divmod(straights,2)[1] == 0:
        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        coordinate=turn.ports[2]
        STRAIGHT=pg.straight(size = (width,meander_length/2), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 90, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        STRAIGHT=pg.straight(size = (width,left/2), layer = 0)
        STRAIGHT.rotate(-90)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
        straight=D.add_ref(STRAIGHT)
    else:
        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        coordinate=turn.ports[2]
        STRAIGHT=pg.straight(size = (width,meander_length/2), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -90, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        STRAIGHT=pg.straight(size = (width,left/2), layer = 0)
        STRAIGHT.rotate(-90)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
        straight=D.add_ref(STRAIGHT)
    #beginpad=D.add_port(name = 'beginpad', midpoint = [-4, 0],  width = 19, orientation = 180)
    #D.add_ref(pr.route_basic(port1 = beginpad, port2 = begin, width_type = 'sine', num_path_pts = 99, layer = 0 ))
    D.add_port(port=straight.ports[1], name='end')
    #D.flatten(single_layer = 0)
    #D.write_gds('survive.gds')
#    qp(D)
    return D
#%% MEANDERED NW SYM
def meandered_nw (straights, turns, left, ratio_radius, width, meander_length):
    left=left;
    s=straights
    t=turns;
    total_steps=s+t;
    c=3e9;
    meander_length=meander_length;
    width=width;
    ratio_radius=ratio_radius;
    D= Device('meandered_NW')
    begin=D.add_port(name = 'begin', midpoint = [0,0],  width = width, orientation = 0)

    STRAIGHT=pg.straight(size = (width,left/2), layer = 0)
    STRAIGHT.rotate(-90)
    STRAIGHT.move(origin = STRAIGHT.ports[2], destination = begin)
    straight=D.add_ref(STRAIGHT)
    
    TURN=pg.turn(straight.ports[1], radius = 3*width, angle = 90, angle_resolution = 2, layer = 0)
    turn=D.add_ref(TURN)
#    qp(D)

    STRAIGHT=pg.straight(size = (width,meander_length/2), layer = 0)
    STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
    straight=D.add_ref(STRAIGHT)
    TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
    turn=D.add_ref(TURN)
    coordinate=turn.ports[2]
#    qp(D)
    while s > 0 and t > -1:
        #        if divmod(x,2)[1] == 0:
        STRAIGHT=pg.straight(size = (width,meander_length), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        s=s-1;
        if s==0 and t==0 :
            break
        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        t=t-1;
        coordinate=turn.ports[2]
        if s==0 and t==0 :
            break
        STRAIGHT=pg.straight(size = (width,meander_length), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        s=s-1;
        if s==0 and t==0 :
            break
        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        t=t-1;
        coordinate=turn.ports[2]
        
    if divmod(straights,2)[1] == 0:
        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        coordinate=turn.ports[2]
        STRAIGHT=pg.straight(size = (width,meander_length/2), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 90, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        STRAIGHT=pg.straight(size = (width,left/2), layer = 0)
        STRAIGHT.rotate(-90)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
        straight=D.add_ref(STRAIGHT)
    else:
        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 180, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        coordinate=turn.ports[2]
        STRAIGHT=pg.straight(size = (width,meander_length/2), layer = 0)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = coordinate)
        straight=D.add_ref(STRAIGHT)
        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -90, angle_resolution = 2, layer = 0)
        turn=D.add_ref(TURN)
        STRAIGHT=pg.straight(size = (width,left/2), layer = 0)
        STRAIGHT.rotate(-90)
        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
        straight=D.add_ref(STRAIGHT)
    #beginpad=D.add_port(name = 'beginpad', midpoint = [-4, 0],  width = 19, orientation = 180)
    #D.add_ref(pr.route_basic(port1 = beginpad, port2 = begin, width_type = 'sine', num_path_pts = 99, layer = 0 ))
    D.add_port(port=straight.ports[1], name='end')
    #D.flatten(single_layer = 0)
    #D.write_gds('survive.gds')
#    qp(D)
    return D

#%% MEANDERED NW ASYM

#def meandered_nw (straights, turns, left, ratio_radius, width, meander_length):
#    left=left;
#    s=straights
#    t=turns;
#    total_steps=s+t;
#    c=3e9;
#    meander_length=meander_length;
#    width=width;
#    ratio_radius=ratio_radius;
#    D= Device('meandered_NW')
#    begin=D.add_port(name = 'begin', midpoint = [0,0],  width = width, orientation = 0)
#
#    TURN=pg.turn(begin, radius = 3*width, angle = 90, angle_resolution = 2, layer = 0)
#    turn=D.add_ref(TURN)
#    qp(D)
#
#    STRAIGHT=pg.straight(size = (width,meander_length/2+left/2), layer = 0)
#    STRAIGHT.move(origin = STRAIGHT.ports[2], destination = turn.ports[2])
#    straight=D.add_ref(STRAIGHT)
#    TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
#    turn=D.add_ref(TURN)
#    coordinate=turn.ports[2]
#    qp(D)
#    while s > 0 and t > -1:
#        #        if divmod(x,2)[1] == 0:
#        STRAIGHT=pg.straight(size = (width,meander_length), layer = 0)
#        STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
#        straight=D.add_ref(STRAIGHT)
#        s=s-1;
#        if s==0 and t==0 :
#            break
#        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 180, angle_resolution = 2, layer = 0)
#        turn=D.add_ref(TURN)
#        t=t-1;
#        coordinate=turn.ports[2]
#        if s==0 and t==0 :
#            break
#        STRAIGHT=pg.straight(size = (width,meander_length), layer = 0)
#        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = coordinate)
#        straight=D.add_ref(STRAIGHT)
#        s=s-1;
#        if s==0 and t==0 :
#            break
#        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
#        turn=D.add_ref(TURN)
#        t=t-1;
#        coordinate=turn.ports[2]
#        
#    if divmod(straights,2)[1] == 0:
#        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -180, angle_resolution = 2, layer = 0)
#        turn=D.add_ref(TURN)
#        coordinate=turn.ports[2]
#        STRAIGHT=pg.straight(size = (width,meander_length/2+left/2), layer = 0)
#        STRAIGHT.move(origin = STRAIGHT.ports[1], destination = coordinate)
#        straight=D.add_ref(STRAIGHT)
#        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 90, angle_resolution = 2, layer = 0)
#        turn=D.add_ref(TURN)
#    else:
#        TURN=pg.turn(straight.ports[2], radius = 3*width, angle = 180, angle_resolution = 2, layer = 0)
#        turn=D.add_ref(TURN)
#        coordinate=turn.ports[2]
#        STRAIGHT=pg.straight(size = (width,meander_length/2+left/2), layer = 0)
#        STRAIGHT.move(origin = STRAIGHT.ports[2], destination = coordinate)
#        straight=D.add_ref(STRAIGHT)
#        TURN=pg.turn(straight.ports[1], radius = 3*width, angle = -90, angle_resolution = 2, layer = 0)
#        turn=D.add_ref(TURN)
##beginpad=D.add_port(name = 'beginpad', midpoint = [-4, 0],  width = 19, orientation = 180)
##D.add_ref(pr.route_basic(port1 = beginpad, port2 = begin, width_type = 'sine', num_path_pts = 99, layer = 0 ))
#    D.add_port(port=turn.ports[2], name='end')
##D.flatten(single_layer = 0)
##D.write_gds('survive.gds')
#    qp(D)
#    return D
    
def trap(bm, bM, h,layer):
    diff=bM-bm
    pointsx = [0,bm,-diff/2+bM,-diff/2]
    pointsy= [0,0,-h,-h]
    D=Device('D')
    D.add_polygon([pointsx,pointsy])
    D.add_port(name = 'narrow', midpoint = [bm/2, 0],  width = bm, orientation = 90)
    D.add_port(name = 'wide', midpoint = [-diff/2+bM/2, -h],  width = bM, orientation = -90)
    D.flatten(single_layer = layer)
    return D


def cpwt(length=1000, width=1000, ratio1=0.8, ratio2=0.8, pnarrow=10, pwide=200, offset=-200):
    CPW=Device('CPW')
    ang=np.degrees(-np.arctan(offset/length))
    pgwide=(pwide+2*pwide*ratio2)
    pgnarrow=pnarrow+2*pnarrow*ratio1
    
    
    if offset == 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio1, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio2, orientation = -90)
        wide=CPW.add_port(name='wide', midpoint=gwide.midpoint, width=pwide, orientation=gwide.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        trace=CPW.add_ref(pg.boolean(ccg,cc,'A-B',0.000001,0))
        CPW.remove(cc)
        CPW.remove(ccg)
        
    
    if offset < 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio1, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gnarrow2=CPW.add_port(name = 'gnarrow2', midpoint = [gnarrow.midpoint[0]-pgnarrow/2*(1-np.cos(np.radians(ang))),gnarrow.midpoint[1]+pgnarrow/2*np.sin(np.radians(ang))],  width = pgnarrow, orientation = 90+ang)
        narrow2=CPW.add_port(name='narrow2', midpoint=gnarrow2.midpoint, width=pnarrow, orientation=gnarrow2.orientation)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio2, orientation = -90)
        gwide2= CPW.add_port(name = 'gwide2', midpoint = [gwide.midpoint[0]-pgwide/2*(1-np.cos(np.radians(ang))) +  offset,gwide.midpoint[1]+pgwide/2*np.sin(np.radians(ang))],  width = pgwide, orientation = -90+ang)
        wide=CPW.add_port(name='wide', midpoint=gwide2.midpoint, width=pwide, orientation=gwide2.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow2, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg2=CPW.add_ref(pr.route_basic(gnarrow2,gwide2, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        turn1=CPW.add_ref(pg.arc(radius =(gnarrow.width-narrow.width)/4 , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn1.move(origin=(turn1.ports[1].midpoint[0]-turn1.ports[1].width/2,turn1.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]-gnarrow.width/2,gnarrow.midpoint[1]))
        turn2=CPW.add_ref(pg.arc(radius =(gnarrow.width-(gnarrow.width-narrow.width)/4) , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn2.move(origin=(turn2.ports[1].midpoint[0]-turn2.ports[1].width/2,turn2.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]+narrow.width/2,gnarrow.midpoint[1]))
        trace=CPW.add_ref(pg.boolean(ccg2,cc,'A-B',0.000001,0))
        CPW.remove(cc)
        CPW.remove(ccg2)
        CPW.remove(ccg)

    if offset > 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio1, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gnarrow2=CPW.add_port(name = 'gnarrow2', midpoint = [gnarrow.midpoint[0]+pgnarrow/2*(1-np.cos(np.radians(ang))),gnarrow.midpoint[1]-pgnarrow/2*np.sin(np.radians(ang))],  width = pgnarrow, orientation = 90+ang)
        narrow2=CPW.add_port(name='narrow2', midpoint=gnarrow2.midpoint, width=pnarrow, orientation=gnarrow2.orientation)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio2, orientation = -90)
        gwide2= CPW.add_port(name = 'gwide2', midpoint = [gwide.midpoint[0]+pgwide/2*(1-np.cos(np.radians(ang))) +  offset,gwide.midpoint[1]-pgwide/2*np.sin(np.radians(ang))],  width = pgwide, orientation = -90+ang)
        wide=CPW.add_port(name='wide', midpoint=gwide2.midpoint, width=pwide, orientation=gwide2.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow2, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg2=CPW.add_ref(pr.route_basic(gnarrow2,gwide2, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        turn1=CPW.add_ref(pg.arc(radius =(gnarrow.width-narrow.width)/4 , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn1.move(origin=(turn1.ports[1].midpoint[0]-turn1.ports[1].width/2,turn1.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]-gnarrow.width/2,gnarrow.midpoint[1]))
        turn2=CPW.add_ref(pg.arc(radius =(gnarrow.width-(gnarrow.width-narrow.width)/4) , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn2.move(origin=(turn2.ports[1].midpoint[0]-turn2.ports[1].width/2,turn2.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]+narrow.width/2,gnarrow.midpoint[1]))
        turn1.reflect((0,0),(0,1))
        turn1.reflect((0,0),(1,0))
        turn2.reflect((0,0),(0,1))
        turn2.reflect((0,0),(1,0))
        trace=CPW.add_ref(pg.boolean(ccg2,cc,'A-B',0.000001,0))
        CPW.remove(cc)
        CPW.remove(ccg2)
        CPW.remove(ccg)
          
    X=Device('trace')
    X.add_ref(CPW)
    narrow=X.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = -90)
    X.flatten()
    return X

def cpwt_au(length=1000, width=1000, ratio1=0.8, ratio2=0.8, pnarrow=10, pwide=200, offset=-200):

    CPW=Device('CPW')
    ang=np.degrees(-np.arctan(offset/length))
    pgwide=(pwide+2*pwide*ratio1)
    pgnarrow=pnarrow+2*pnarrow*ratio2
    
    
    if offset == 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio2, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio1, orientation = -90)
        wide=CPW.add_port(name='wide', midpoint=gwide.midpoint, width=pwide, orientation=gwide.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        trace=CPW.add_ref(pg.boolean(ccg,cc,'A-B',0.0001,0))
        CPW.remove(cc)
        CPW.remove(ccg)
        
    
    if offset < 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio2, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gnarrow2=CPW.add_port(name = 'gnarrow2', midpoint = [gnarrow.midpoint[0]-pgnarrow/2*(1-np.cos(np.radians(ang))),gnarrow.midpoint[1]+pgnarrow/2*np.sin(np.radians(ang))],  width = pgnarrow, orientation = 90+ang)
        narrow2=CPW.add_port(name='narrow2', midpoint=gnarrow2.midpoint, width=pnarrow, orientation=gnarrow2.orientation)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio1, orientation = -90)
        gwide2= CPW.add_port(name = 'gwide2', midpoint = [gwide.midpoint[0]-pgwide/2*(1-np.cos(np.radians(ang))) +  offset,gwide.midpoint[1]+pgwide/2*np.sin(np.radians(ang))],  width = pgwide, orientation = -90+ang)
        wide=CPW.add_port(name='wide', midpoint=gwide2.midpoint, width=pwide, orientation=gwide2.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow2, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg2=CPW.add_ref(pr.route_basic(gnarrow2,gwide2, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        turn1=CPW.add_ref(pg.arc(radius =(gnarrow.width-narrow.width)/4 , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn1.move(origin=(turn1.ports[1].midpoint[0]-turn1.ports[1].width/2,turn1.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]-gnarrow.width/2,gnarrow.midpoint[1]))
        turn2=CPW.add_ref(pg.arc(radius =(gnarrow.width-(gnarrow.width-narrow.width)/4) , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn2.move(origin=(turn2.ports[1].midpoint[0]-turn2.ports[1].width/2,turn2.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]+narrow.width/2,gnarrow.midpoint[1]))
        trace=CPW.add_ref(pg.boolean(ccg2,cc,'A-B',0.0001,0))
        CPW.remove(cc)
        CPW.remove(ccg2)
        CPW.remove(ccg)

    if offset > 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio2, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gnarrow2=CPW.add_port(name = 'gnarrow2', midpoint = [gnarrow.midpoint[0]+pgnarrow/2*(1-np.cos(np.radians(ang))),gnarrow.midpoint[1]-pgnarrow/2*np.sin(np.radians(ang))],  width = pgnarrow, orientation = 90+ang)
        narrow2=CPW.add_port(name='narrow2', midpoint=gnarrow2.midpoint, width=pnarrow, orientation=gnarrow2.orientation)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio1, orientation = -90)
        gwide2= CPW.add_port(name = 'gwide2', midpoint = [gwide.midpoint[0]+pgwide/2*(1-np.cos(np.radians(ang))) +  offset,gwide.midpoint[1]-pgwide/2*np.sin(np.radians(ang))],  width = pgwide, orientation = -90+ang)
        wide=CPW.add_port(name='wide', midpoint=gwide2.midpoint, width=pwide, orientation=gwide2.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow2, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg2=CPW.add_ref(pr.route_basic(gnarrow2,gwide2, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        turn1=CPW.add_ref(pg.arc(radius =(gnarrow.width-narrow.width)/4 , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn1.move(origin=(turn1.ports[1].midpoint[0]-turn1.ports[1].width/2,turn1.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]-gnarrow.width/2,gnarrow.midpoint[1]))
        turn2=CPW.add_ref(pg.arc(radius =(gnarrow.width-(gnarrow.width-narrow.width)/4) , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn2.move(origin=(turn2.ports[1].midpoint[0]-turn2.ports[1].width/2,turn2.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]+narrow.width/2,gnarrow.midpoint[1]))
        turn1.reflect((0,0),(0,1))
        turn1.reflect((0,0),(1,0))
        turn2.reflect((0,0),(0,1))
        turn2.reflect((0,0),(1,0))
        trace=CPW.add_ref(pg.boolean(ccg2,cc,'A-B',0.00001,0))
        CPW.remove(cc)
        CPW.remove(ccg2)
        CPW.remove(ccg)
          
    X=Device('trace')
    X.add_ref(CPW)
    narrow=X.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = -90)
    X.flatten()
    return X




def cpwg(length=1000, width=1000, ratio=0.8, pnarrow=10, pwide=200, offset=-200):

    CPW=Device('CPW')
    ang=np.degrees(-np.arctan(offset/length))
    pgwide=(pwide+2*pwide*ratio)
    pgnarrow=pnarrow+2*pnarrow*ratio
    
    
    if offset == 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio, orientation = -90)
        wide=CPW.add_port(name='wide', midpoint=gwide.midpoint, width=pwide, orientation=gwide.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        trace=CPW.add_ref(pg.boolean(ccg,cc,'A-B',0.0001,0))
        CPW.remove(cc)
        CPW.remove(ccg)
        
    
    if offset < 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gnarrow2=CPW.add_port(name = 'gnarrow2', midpoint = [gnarrow.midpoint[0]-pgnarrow/2*(1-np.cos(np.radians(ang))),gnarrow.midpoint[1]+pgnarrow/2*np.sin(np.radians(ang))],  width = pgnarrow, orientation = 90+ang)
        narrow2=CPW.add_port(name='narrow2', midpoint=gnarrow2.midpoint, width=pnarrow, orientation=gnarrow2.orientation)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio, orientation = -90)
        gwide2= CPW.add_port(name = 'gwide2', midpoint = [gwide.midpoint[0]-pgwide/2*(1-np.cos(np.radians(ang))) +  offset,gwide.midpoint[1]+pgwide/2*np.sin(np.radians(ang))],  width = pgwide, orientation = -90+ang)
        wide=CPW.add_port(name='wide', midpoint=gwide2.midpoint, width=pwide, orientation=gwide2.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow2, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg2=CPW.add_ref(pr.route_basic(gnarrow2,gwide2, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        turn1=CPW.add_ref(pg.arc(radius =(gnarrow.width-narrow.width)/4 , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn1.move(origin=(turn1.ports[1].midpoint[0]-turn1.ports[1].width/2,turn1.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]-gnarrow.width/2,gnarrow.midpoint[1]))
        turn2=CPW.add_ref(pg.arc(radius =(gnarrow.width-(gnarrow.width-narrow.width)/4) , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn2.move(origin=(turn2.ports[1].midpoint[0]-turn2.ports[1].width/2,turn2.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]+narrow.width/2,gnarrow.midpoint[1]))
        trace=CPW.add_ref(pg.boolean(ccg2,cc,'A-B',0.0001,0))
        CPW.remove(cc)
        CPW.remove(ccg2)
        CPW.remove(ccg)

    if offset > 0:
        gnarrow=CPW.add_port(name = 'gnarrow', midpoint = [0,0],  width = pnarrow+2*pnarrow*ratio, orientation = 90)
        narrow=CPW.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = 90)
        gnarrow2=CPW.add_port(name = 'gnarrow2', midpoint = [gnarrow.midpoint[0]+pgnarrow/2*(1-np.cos(np.radians(ang))),gnarrow.midpoint[1]-pgnarrow/2*np.sin(np.radians(ang))],  width = pgnarrow, orientation = 90+ang)
        narrow2=CPW.add_port(name='narrow2', midpoint=gnarrow2.midpoint, width=pnarrow, orientation=gnarrow2.orientation)
        gwide=CPW.add_port(name = 'gwide', midpoint = [0,length],  width = pwide+2*pwide*ratio, orientation = -90)
        gwide2= CPW.add_port(name = 'gwide2', midpoint = [gwide.midpoint[0]+pgwide/2*(1-np.cos(np.radians(ang))) +  offset,gwide.midpoint[1]-pgwide/2*np.sin(np.radians(ang))],  width = pgwide, orientation = -90+ang)
        wide=CPW.add_port(name='wide', midpoint=gwide2.midpoint, width=pwide, orientation=gwide2.orientation)
        cc=CPW.add_ref(pr.route_basic(narrow2, wide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg2=CPW.add_ref(pr.route_basic(gnarrow2,gwide2, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        ccg=CPW.add_ref(pr.route_basic(gnarrow,gwide, path_type = 'straight', width_type = 'straight', num_path_pts = 99, layer=0))
        turn1=CPW.add_ref(pg.arc(radius =(gnarrow.width-narrow.width)/4 , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn1.move(origin=(turn1.ports[1].midpoint[0]-turn1.ports[1].width/2,turn1.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]-gnarrow.width/2,gnarrow.midpoint[1]))
        turn2=CPW.add_ref(pg.arc(radius =(gnarrow.width-(gnarrow.width-narrow.width)/4) , width = (gnarrow.width-narrow.width)/2, theta = ang, start_angle = 0, angle_resolution = 0.00001, layer = 0))
        turn2.move(origin=(turn2.ports[1].midpoint[0]-turn2.ports[1].width/2,turn2.ports[1].midpoint[1]),destination=(gnarrow.midpoint[0]+narrow.width/2,gnarrow.midpoint[1]))
        turn1.reflect((0,0),(0,1))
        turn1.reflect((0,0),(1,0))
        turn2.reflect((0,0),(0,1))
        turn2.reflect((0,0),(1,0))
        trace=CPW.add_ref(pg.boolean(ccg2,cc,'A-B',0.00001,0))
        CPW.remove(cc)
        CPW.remove(ccg2)
        CPW.remove(ccg)
        
    BOX=Device('BOX')
    rect=BOX.add_ref(pg.rectangle(size=(width,length),layer=0))
    rect.move(origin=rect.center, destination=(0,length/2))   
    trace=pg.boolean(rect,CPW,'A-B',0.0001,0) 
    X=Device('trace')
    X.add_ref(trace)
    narrow=X.add_port(name = 'narrow', midpoint = [0,0],  width = pnarrow, orientation = -90)
    X.flatten()
        #    X.rotate(angle=-ang, center=(pin.midpoint[0],pin.midpoint[1]))
    return X

'''
def grating(num_periods = 20, period = 0.75, fill_factor = 0.5, width_grating = 5, length_taper = 10, width = 0.4, partial_etch = False):
    #returns a fiber grating
    G = Device('grating')

    # make the deep etched grating
    if partial_etch is False:
        # make the grating teeth
        for i in range(num_periods):
            cgrating = G.add_ref(pg.compass(size=[period*fill_factor,width_grating], layer = 0))
            cgrating.x+=i*period

        # make the taper
        tgrating = G.add_ref(pg.taper(length = length_taper, width1 = width_grating, width2 = width, port = None, layer = 0))
        tgrating.xmin = cgrating.xmax
        # define the port of the grating
        p = G.add_port(port = tgrating.ports[2], name = 1)
    # make a partially etched grating
    if partial_etch is True:
        # hard coded overlap
            partetch_overhang = 5
            # make the etched areas (opposite to teeth)
            for i in range(num_periods):
                cgrating = G.add_ref(pg.compass(size=[period*(1-fill_factor),width_grating+partetch_overhang*2]), layer = 1)
                cgrating.x+=i*period
                        # define the port of the grating
            p = G.add_port(port = cgrating.ports['E'], name = 1)
            p.midpoint=p.midpoint+np.array([(1-fill_factor)*period,0])

        #draw the deep etched square around the grating
            deepbox = G.add_ref(pg.compass(size=[num_periods*period, width_grating]), layer=0)
    return G'''
