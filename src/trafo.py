from numpy import *
from math import *

import sys, os

def rotationMatrix(angle, axis):
    c, mc = cos(angle), 1-cos(angle)
    s = sin(angle)
    l = sqrt(dot(array(axis), array(axis)))
    x, y, z = array(axis)/l
    r = array([
        [x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
        [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
        [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
        [0, 0, 0, 1]])
    return r.T

def scaleMatrix(sx, sy, sz):
    s = array([[sx, 0, 0, 0],
               [0, sy, 0, 0],
               [0, 0, sz, 0],
               [0, 0, 0, 1]])
    return s

def translationMatrix(tx, ty, tz):
    t = array([[1, 0, 0, tx],
                [0, 1, 0, ty],
                [0, 0, 1, tz],
                [0, 0, 0, 1]])
    return t

def lookAtMatrix(ex, ey, ez, cx, cy, cz, ux, uy, uz):
    e = array([ex, ey, ez])
    c = array([cx, cy, cz])
    up = array([ux, uy, uz])

    #normalize
    uplength = sqrt(dot(up, up))
    up = up / uplength
    
    # viewdirection
    f = c-e
    flength = sqrt(dot(f,f))
    f = f / flength

    s = cross(f, up)
    slength = sqrt(dot(s, s))
    s = s /slength

    u = cross(s, f)
    la = array([
        [s[0], s[1], s[2], -dot(s,e)],
        [u[0], u[1], u[2], -dot(u,e)],
        [-f[0], -f[1], -f[2], dot(f,e)],
        [0, 0, 0, 1]])

    return la

def perspectiveMatrix(fov, aspect, zNear, zFar):
    f = 1.0/tan(fov/2.0)
    aspect = float(aspect)
    zNear = float(zNear)
    zFar = float(zFar)
    p = array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (zFar+zNear)/(zNear-zFar), (2*zFar*zNear)/(zNear- zFar)],
        [0, 0, -1, 0]])
    return p
