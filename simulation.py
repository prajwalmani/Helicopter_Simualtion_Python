# -*- coding: utf-8 -*-
import sys, os
from OpenGL.arrays import vbo
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
from numpy import *
from math import *

import itertools

from scene import Scene, Heli
from controller import Controller
from camera import CameraType
import trafo

WIDTH, HEIGHT = 1000, 1000

# constants
FOV = 45
TIMER_MS = 10
# initial values
aspect = WIDTH/float(HEIGHT)

models = []
skybox_01_info = ('data/skybox/01/', '.png')
skybox_02_info = ('data/skybox/02/', '.png')
helicopter_info = ('data/helicopter/','HELICOPTER500D.obj')

def display():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    drawScene()
    glutSwapBuffers()

def drawScene():
    global scene
    scene.draw()

def reshape(width, height):
    global WIDTH, HEIGHT
    
    WIDTH, HEIGHT = width, height
    aspect = width/float(height) if height > 0 else 1.0
    glViewport(0, 0, width, height)
    scene.updateProjection(FOV, aspect)
    
def initGL(width, height):
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def initScene():
    global scene
    scene = Scene(FOV, aspect)
    
    scene.addCamera(CameraType.FIX)
    scene.addCamera(CameraType.FOLLOW)
    scene.addCamera(CameraType.THIRD_PERSON)
    
    scene.addSkybox(skybox_01_info)   
    scene.addSkybox(skybox_02_info)
    
    scene.addHelicopter(helicopter_info)

def animation(value):
    scene.helicopter.doRotor()
    scene.helicopter.fly()
    glutTimerFunc(TIMER_MS, animation, value)
    glutPostRedisplay()

def main():
    global helicopter_info
    args = sys.argv
    objpath = None
    if len(args) == 2:
        objpath = args[1]
        path = os.path.split(objpath)
        helicopter_info = (path[0] + "/", path[1])
        
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("Helicopter")

    initScene()
    controller = Controller(scene)

    glutDisplayFunc(display)     #register display function
    glutReshapeFunc(reshape)     #register reshape function
    glutKeyboardFunc(controller.handleKeyDown) #register keyboard function
    glutKeyboardUpFunc(controller.handleKeyUp) #register keyboard function
    glutTimerFunc(TIMER_MS, animation, 0)
    #glutIdleFunc(idlefunc)

    initGL(WIDTH,HEIGHT) #initialize OpenGL state
    glutMainLoop() #start even processing

if __name__ == "__main__":
   main()
