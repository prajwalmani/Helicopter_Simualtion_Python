import sys, time
from OpenGL.GLUT import *

ttime = 0

class Controller(object):
    def __init__(self, scene):
        self.scene = scene
        self.pressedKeys = set()

    def handleKeyDown(self, key, x, y):
        key=key.decode('utf-8')
        if key == chr(27):
            sys.exit()
        scene = self.scene
        helicopter = scene.helicopter

        if key == 'c':
            scene.switchCam()

        if key == '1':
            scene.switchSky()
        if key in 'adjlikws':
            self.pressedKeys.add(key)

        if key in 'ad':
            global ttime
            ttime = time.time()
            
        for k in self.pressedKeys:                
            if k == 'a': 
                helicopter.gier(False)
            if k == 'd':
                helicopter.gier(True)

            if k == 'j': 
                helicopter.roll(True)
            if k == 'l':
                helicopter.roll(False)

            if k == 'i': 
                helicopter.nick(True)
            if k == 'k':
                helicopter.nick(False)

            if k == 'w':
                helicopter.pitch(True)
            if k == 's':
                helicopter.pitch(False)

    def handleKeyUp(self, key, x, y):
        scene = self.scene
        helicopter = scene.helicopter
        key=key.decode('utf-8')
        if key in 'ad':
            x = time.time()-ttime
            if x > 0.05:
                helicopter.gierSwingout()
    
        if key in 'adjlikws':
            self.pressedKeys.remove(key)
