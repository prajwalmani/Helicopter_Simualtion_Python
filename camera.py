from numpy import *
from math import *
import trafo

def enum(**enums):
    return type('Enum', (), enums)

CameraType = enum(FIX = 1, FOLLOW = 2, THIRD_PERSON = 3)

class Camera(object):
    INIT_EYE = [0, 0, 2]
    INIT_CENTER = [0, 0, -1]
    INIT_UP = [0, 1, 0]
    
    def __init__(self, *information):     
        param_count = len(information)
        self.e = information[0] if param_count else Camera.INIT_EYE
        self.c = information[1] if param_count else Camera.INIT_CENTER
        self.up = information[2] if param_count else Camera.INIT_UP

    def getLookAt(self):
        return trafo.lookAtMatrix(self.e[0],self.e[1],self.e[2], self.c[0], self.c[1], self.c[2], self.up[0], self.up[1], self.up[2])

    def update(self, helipos, orientation):
        return

class ThirdPersonCamera(Camera):
    INIT_DIR = [0, 0, -1, 0]
    INIT_DIST = 3.0
    
    def __init__(self, *information):
        param_count = len(information)
        if param_count == 0:
            self.third_person_dir = array(ThirdPersonCamera.INIT_DIR)
            self.third_person_dist = float(ThirdPersonCamera.INIT_DIST)
            Camera.__init__(self) 
        if param_count == 2:
            self.third_person_dir = array(information[0])
            self.third_person_dist = float(information[1])
            Camera.__init__(self)
        if param_count == 3:
            self.third_person_dir = array(ThirdPersonCamera.INIT_DIR)
            self.third_person_dist = float(ThirdPersonCamera.INIT_DIST)
            Camera.__init__(self, *information) 
        if param_count == 5:
            self.third_person_dir = array(ThirdPersonCamera.INIT_DIR)
            self.third_person_dist = float(ThirdPersonCamera.INIT_DIST)
            Camera.__init__(self, *information[:3]) 

    def update(self, helipos, orientation):
        self.c = helipos
        direction = dot(orientation, self.third_person_dir)
        direction[1] = 0
        self.e = (array(helipos) + (self.third_person_dist * direction)[:3]).tolist()
        self.up = [0,1,0]


class FixCamera(Camera):
    def __init__(self, *information):
        Camera.__init__(self, *information)
        

class FollowCamera(Camera):
    def __init__(self, *information):
        Camera.__init__(self, *information)

    def update(self, helipos, orientation):
        self.c = helipos

