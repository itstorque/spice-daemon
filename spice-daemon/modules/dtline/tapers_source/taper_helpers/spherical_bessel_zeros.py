#! /usr/bin/env python

# from Scipy Cookbook

### recursive method: computes zeros ranges of Jn(r,n) from zeros of Jn(r,n-1)
### (also for zeros of (rJn(r,n))')
### pros : you are certain to find the right zeros values;
### cons : all zeros of the n-1 previous Jn have to be computed;
### note : Jn(r,0) = sin(r)/r

from numpy import arange, pi, sqrt, zeros
from scipy.special import jv, jvp
from scipy.optimize import brentq
from sys import argv
from numpy import float32

def Jn(r,n):
  return (sqrt(pi/(2*r))*jv(n+0.5,r))
def Jn_zeros(n,nt):
  zerosj = zeros((n+1, nt), dtype=float32)
  zerosj[0] = arange(1,nt+1)*pi
  points = arange(1,nt+n+1)*pi
  racines = zeros(nt+n, dtype=float32)
  for i in range(1,n+1):
    for j in range(nt+n-i):
      foo = brentq(Jn, points[j], points[j+1], (i,))
      racines[j] = foo
    points = racines
    zerosj[i][:nt] = racines[:nt]
  return (zerosj)

def rJnp(r,n):
  return (0.5*sqrt(pi/(2*r))*jv(n+0.5,r) + sqrt(pi*r/2)*jvp(n+0.5,r))
def rJnp_zeros(n,nt):
  zerosj = zeros((n+1, nt), dtype=float32)
  zerosj[0] = (2.*arange(1,nt+1)-1)*pi/2
  points = (2.*arange(1,nt+n+1)-1)*pi/2
  racines = zeros(nt+n, dtype=float32)
  for i in range(1,n+1):
    for j in range(nt+n-i):
      foo = brentq(rJnp, points[j], points[j+1], (i,))
      racines[j] = foo
    points = racines
    zerosj[i][:nt] = racines[:nt]
  return (zerosj)


ns = range(2, 11)
all_zeros = []
for n in ns:
    all_zeros.append(Jn_zeros(n, 1)[n][0])

# print(all_zeros)

'''
n = int(argv[1])  # n'th spherical bessel function
nt = int(argv[2]) # number of zeros to be computed

dr = 0.01
eps = dr/1000

jnz = Jn_zeros(n,nt)[n]
r1 = arange(eps,jnz[len(jnz)-1],dr)
jnzp = rJnp_zeros(n,nt)[n]
r2 = arange(eps,jnzp[len(jnzp)-1],dr)

grid(True)
plot(r1,Jn(r1,n),'b', r2,rJnp(r2,n),'r')
title((str(nt)+' first zeros'))
legend((r'$j_{'+str(n)+'}(r)$', r'$(rj_{'+str(n)+'}(r))\'$'))
plot(jnz,zeros(len(jnz)),'bo') #, jnzp,zeros(len(jnzp)),'rd')
print(jnz)
gca().xaxis.set_minor_locator(MultipleLocator(1))
# gca().xaxis.set_minor_formatter(FormatStrFormatter('%d'))
show()'''