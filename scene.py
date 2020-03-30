# -*- coding: utf-8 -*-
import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import *
from PIL import Image
from numpy import *
from math import *

import itertools

from camera import *
import objloader
import sender
import trafo


shaderdir = "shader/"
vert_ext = ".vert"
frag_ext = ".frag"

FORCE_OF_GRAVITY = 0.98

X_AXIS = [1,0,0]
Y_AXIS = [0,1,0]
Z_AXIS = [0,0,1]
GRAVITY = [0,-FORCE_OF_GRAVITY,0]

DEFAULT_ORIENTATION = identity(4)


class SimpleObjObject(object):
    def __init__(self, path, filename):
        self.position = [0,0,0]
        self.orientation = DEFAULT_ORIENTATION
        obj_data = objloader.ReadObj(path, filename)
        mat_data = objloader.SimpleObjData(obj_data)
        self.model = Model3D(mat_data)

    def draw(self, camera, projection):
        mvMat = camera.getLookAt()
        mvMat = dot(mvMat, trafo.translationMatrix(*self.position))
        mvMat = dot(mvMat, self.orientation)
        self.model.draw(camera, projection, mvMat)
        
class Heli(object):
    BODY = ['500-D_Luz_Verde', '500-D_Lineas', '500-D_Luz_Roja', '500-D_Negro', '500-D___500-D', '500-D_Matricula']
    GLASS = ['500-D_Cristal_no', '500-D_Cristal_Ve']
    ROTOR = ['500-D_Negro1', '500-D_Rojo']
    ROTOR_BACK = ['500-D_Blanco']
    HUBEL = ['500-D_Rojo']

    GIER_ANGLE = radians(.3)
    ROLL_ANGLE = radians(.5)
    NICK_ANGLE = radians(.5)
    MAX_ANGLE_GIER = radians(5)
    MAX_ANGLE_ROLL = radians(45)
    MAX_ANGLE_NICK = radians(60)
    
    PITCH_STEP = 200.0
    SPEED = 0.1
    WEIGHT = 1000.0
    MAX_POWER = 18000.0

    def __init__(self, path, filename):
        self.orientation = DEFAULT_ORIENTATION
        self.position = [0,0,0]
        self.up = [0,1,0]
        self.dir = [0,0,1]
        
        self.x_angle = 0.0
        self.z_angle = 0.0
        self.rot_angle = 0.0

        self.lift = FORCE_OF_GRAVITY
        self.liftPower = FORCE_OF_GRAVITY * 10000
        
        self.can_move_up = True
        self.can_move_down = True
        self.can_move_forward = True
        self.can_move_backward = True
        self.can_move_right = True
        self.can_move_left = True
        self.rotSpeed = self.liftPower * 0.001
        self.nickSpeed = 0.0

        self._initModels(objloader.ReadObj(path, filename))

    def _initModels(self, obj_data):
        self.bb = obj_data.bb
        mat_body = objloader.MaterialData(obj_data, Heli.BODY)
        mat_glass = objloader.MaterialData(obj_data, Heli.GLASS)
        mat_huble = objloader.MaterialData(obj_data, Heli.HUBEL)
        mat_rotor = objloader.MaterialData(obj_data, Heli.ROTOR)
        mat_rotor_back = objloader.MaterialData(obj_data, Heli.ROTOR_BACK, minindex=2720)
        mat_nose = objloader.MaterialData(obj_data, Heli.ROTOR_BACK, maxindex=2719)
        mat_rotor.center = mat_huble.center
        self.rotor = Model3D(mat_rotor, rotation_axis=Y_AXIS)
        self.rotor_back = Model3D(mat_rotor_back, rotation_axis=X_AXIS)
        self.models=[]
        self.models.append(Model3D(mat_nose))
        self.models.append(Model3D(mat_body))
        self.models.append(Model3D(mat_glass))
        
    def draw(self, camera, projection):
        camera.update(self.position, self.orientation) 

        mvMat = camera.getLookAt()
        mvMat = dot(mvMat, trafo.translationMatrix(*self.position))
        mvMat = dot(mvMat, self.orientation)

        self.rotor.draw(camera, projection, mvMat)
        self.rotor_back.draw(camera, projection, mvMat)
        
        for model in self.models:
            model.draw(camera, projection, mvMat)
        
    def _rotate(self, rot_angle, axis, curr_angle=None):
        self.orientation = dot(self.orientation, trafo.rotationMatrix(rot_angle, axis))

    def _rotate_global(self, rot_angle, axis, curr_angle=None):
        self.orientation = dot(trafo.rotationMatrix(rot_angle, axis), self.orientation)

    def nick(self, forwards):
        rot_angle = Heli.NICK_ANGLE if forwards else -Heli.NICK_ANGLE
        self.x_angle += rot_angle
        if self.x_angle > Heli.MAX_ANGLE_NICK:
            self.x_angle = Heli.MAX_ANGLE_NICK
        elif self.x_angle < -Heli.MAX_ANGLE_NICK:
            self.x_angle = -Heli.MAX_ANGLE_NICK
        else:
            self._rotate(-rot_angle, X_AXIS)

    def roll(self, right):
        rot_angle = Heli.ROLL_ANGLE if right else -Heli.ROLL_ANGLE
        self.z_angle += rot_angle
        if self.z_angle > Heli.MAX_ANGLE_ROLL:
            self.z_angle = Heli.MAX_ANGLE_ROLL
        elif self.z_angle < -Heli.MAX_ANGLE_ROLL:
            self.z_angle = -Heli.MAX_ANGLE_ROLL
        else:
            self._rotate(rot_angle, Z_AXIS)
        
    def gier(self, right):
        self.rot_angle += Heli.GIER_ANGLE if right else -Heli.GIER_ANGLE
        if self.rot_angle > Heli.MAX_ANGLE_GIER:
            self.rot_angle = Heli.MAX_ANGLE_GIER
        elif self.rot_angle < -Heli.MAX_ANGLE_GIER:
            self.rot_angle = -Heli.MAX_ANGLE_GIER
        self._rotate_global(self.rot_angle, Y_AXIS)

    def gierSwingout(self):
        self.rot_angle = 0.0

    def pitch(self, up):
        self.liftPower += Heli.PITCH_STEP if up else -Heli.PITCH_STEP
        if self.liftPower <= 0.0:
            self.liftPower = 200.0
        elif self.liftPower >= Heli.MAX_POWER:
            self.liftPower = Heli.MAX_POWER
        self.lift = (self.liftPower/Heli.WEIGHT) * 0.1

    def fly(self):
        weighted_up = self.updateUp()* self.lift
        #check top/bottom docking
        top_blocked = self.movesUp(weighted_up) and not self.can_move_up
        bottom_blocked = not self.movesUp(weighted_up) and not self.can_move_down
        if top_blocked or bottom_blocked:
            weighted_up[1] = FORCE_OF_GRAVITY
        #check side docking
        right_blocked = self.movesRight(weighted_up) and not self.can_move_right
        left_blocked = not self.movesRight(weighted_up) and not self.can_move_left
        front_blocked = self.movesFront(weighted_up) and not self.can_move_forward
        back_blocked = not self.movesFront(weighted_up) and not self.can_move_backward

        gravity = array(GRAVITY) 
        pos = array(self.position)
        self.dir = weighted_up + gravity
        
        if right_blocked:
            self.dir[0] = 0
        if left_blocked:
            self.dir[0] = 0
        if front_blocked:
            self.dir[2] = 0
        if back_blocked:
            self.dir[2] = 0
        self.position = (pos +  Heli.SPEED * self.dir).tolist()

    def movesRight(self, weighted_up):
        return weighted_up[0] > 0
    
    def movesUp(self, weighted_up):
        return weighted_up[1] > FORCE_OF_GRAVITY

    def movesFront(self, weighted_up):
        return weighted_up[2] > 0

    def updateUp(self):
        up = self.orientation.T[1][:3]
        uplength = sqrt(dot(up, up))
        self.up = up / uplength
        return up
        
    def doRotor(self):
        fac = self.lift * 15
        self.rotor.angle = (self.rotor.angle + fac) % 360
        self.rotor_back.angle = (self.rotor_back.angle + 20) % 360

class Model3D(object):
    _VARNAME_LIST =  ["mvMatrix", "mvpMatrix", "normalMatrix", "diffuseColor", "ambientColor", "specularColor", "alpha", "shininess","hasTexture",  "lightPosition"]
    
    def __init__(self, mat_obj, rotation_axis=Y_AXIS):
        self.mat_obj = mat_obj
        self.face_groups = mat_obj.face_groups
        self.center = mat_obj.center
        self.materials = mat_obj.materials
        
        self.orientation = DEFAULT_ORIENTATION
        self.rotation_axis = rotation_axis
        self.angle = 0
                
        self.program = self._init_shader("textureshader")
        self.shadersender = sender.Sender(self.program, Model3D._VARNAME_LIST)
        self._load_materials(self.materials)

    def _load_materials(self, materials):
        for material in materials.values():
            if material.texture_filename: # wenn eine Textur vorhanden ist?!
                im = Image.open(material.texture_filename)
                material.texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, material.texture_id)
                glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.size[0], im.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, array(im)[::-1,:].tostring())
        
    def _init_shader(self, shadername):
        shaderpath = shaderdir + shadername
        vertexShader = open(shaderpath + vert_ext).read()
        fragmentShader = open(shaderpath + frag_ext).read()
        return compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER),
                                     compileShader(fragmentShader, GL_FRAGMENT_SHADER))
        

    def draw(self, camera, projection, mvMat):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glEnable(GL_TEXTURE_2D)

        for face_group in self.face_groups.values():
            material = self.materials[face_group.material_name]
            
            vb = self.mat_obj.getVBO(material.name)
            if material.alpha < 1.0:
                glEnable(GL_BLEND) ## for opacity
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            modelview = matrix.copy(mvMat) # sonst hämmert man auf der helimatrix rum, die man nachher noch braucht
            modelview = dot(modelview, trafo.translationMatrix(self.center[0], self.center[1], self.center[2]))
            modelview = dot(modelview, dot(trafo.rotationMatrix(radians(self.angle), self.rotation_axis), self.orientation))
            modelview = dot(modelview, trafo.translationMatrix(-self.center[0], -self.center[1], -self.center[2]))
            
            normalMat = linalg.inv(modelview[0:3,0:3]).T

            mvpMat = dot(projection, modelview)
            
            glUseProgram(self.program)

            s = self.shadersender
            s.sendMat4("mvMatrix", mvMat)
            s.sendMat4("mvpMatrix", mvpMat)
            s.sendMat3("normalMatrix", normalMat)
            s.sendVec4("diffuseColor", material.diffuse)
            s.sendVec4("ambientColor", material.ambient)
            s.sendVec4("specularColor", material.specular)
            s.sendValue("shininess", material.exponent)
            s.sendValue("alpha", material.alpha)
            s.sendVec3("lightPosition", [0,70.0,70.0])
            s.sendValue("hasTexture", material.has_texture())
            
            vb.bind()

            glVertexPointer(3, GL_FLOAT, 36, vb)
            glTexCoordPointer(3, GL_FLOAT, 36, vb + 12)
            glNormalPointer(GL_FLOAT, 36, vb + 24)
                
            glBindTexture(GL_TEXTURE_2D, material.texture_id)

            glDrawArrays(GL_TRIANGLES, 0, int(len(vb) / 3))
            vb.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)


    def __del__(self):
        self._free_resources()


    def _free_resources(self):
        for material in self.materials.values():
            if material.texture_id is not None:
                glDeleteTextures(material.texture_id)
        self.materials.clear()
        self.face_groups.clear()


            
class Camera(object):
    INIT_EYE = [0, 0, 2]
    INIT_CENTER = [0, 0, -1]
    INIT_UP = [0, 1, 0]

    INIT_DIR = [0, 0, -1, 0]
    INIT_DIST = 3.0

    FIX_CAM, FOLLOW_CAM, THIRD_PERSON_CAM = 0, 1, 2
    
    def __init__(self, cam_type, *information):
        self.cam_type = cam_type
        
        param_count = len(information)

        if param_count in (0,2):
            self.e = Camera.INIT_EYE
            self.c = Camera.INIT_CENTER
            self.up = Camera.INIT_UP
        elif param_count in (3,5):
            self.e = information[0]
            self.c = information[1]
            self.up = information[2]

        if cam_type == Camera.THIRD_PERSON_CAM:
            if param_count in (2,5):
                self.third_person_dir = array(information[-2])
                self.third_person_dist = float(information[-1])
            elif param_count in (0,3):
                self.third_person_dir = array(Camera.INIT_DIR)
                self.third_person_dist = float(Camera.INIT_DIST)

    def getLookAt(self):
        return trafo.lookAtMatrix(self.e[0],self.e[1],self.e[2], self.c[0], self.c[1], self.c[2], self.up[0], self.up[1], self.up[2])
        
    def update(self, helipos, orientation): 
        if self.cam_type == Camera.FIX_CAM:
            return
        self.c = helipos
        if self.cam_type == Camera.THIRD_PERSON_CAM:
            direction = dot(orientation, self.third_person_dir)
            direction[1] = 0
            self.e = (array(helipos) + (self.third_person_dist * direction)[:3]).tolist()
            self.up = [0,1,0]




       
class TexturedQuad(object):
    _VARNAME_LIST = ["mvMatrix", "mvpMatrix"]
    _texture_coords = [[0,0], [1,0], [1,1], [0,1]]
    
    def __init__(self, imgpath, vertex_coords):
        im = Image.open(imgpath).convert('RGBA')
        self.image = array(im)[::-1, :].tostring()
        self.xsize, self.ysize = im.size
        self.texture_id = glGenTextures(1)

        self.data = [vertex_coords[i] + TexturedQuad._texture_coords[i] for i in range(4)] 
        self.vb = vbo.VBO(array(self.data, "f"))

        self.program = self._init_shader("simpletexture")
        self.shadersender = sender.Sender(self.program, TexturedQuad._VARNAME_LIST)

        self._bind_textures()


    def _init_shader(self, shadername):
        shaderpath = shaderdir + shadername

        vertexShader = open(shaderpath + vert_ext).read()
        fragmentShader = open(shaderpath + frag_ext).read()
        return compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER),
                                     compileShader(fragmentShader, GL_FRAGMENT_SHADER))

    def _bind_textures(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) #CLAMP_TO_EDGE sodass kanten nicht sichtbar sind!
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.xsize, self.ysize, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.image)


    def draw(self, camera, projection):
        vb = self.vb

        mvMat = camera.getLookAt()
        mvpMat = dot(projection, mvMat)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        vb.bind()

        glUseProgram(self.program)
        s = self.shadersender
        s.sendMat4("mvMatrix", mvMat)
        s.sendMat4("mvpMatrix", mvpMat)

        glVertexPointer(3, GL_FLOAT, 20, vb)
        glTexCoordPointer(2, GL_FLOAT, 20, vb+12)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glDrawArrays(GL_QUADS, 0, len(self.data))
        
        vb.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)



class Skybox(object):
    D = 100.0 # war mal 2.5
    FRONT = [[D,-D,-D], [-D,-D,-D], [-D,D,-D], [D,D,-D]]
    LEFT = [[-D,-D,-D], [-D,-D,D], [-D,D,D],[-D,D,-D]] 
    BACK = [[-D,-D,D], [D,-D,D], [D,D,D], [-D,D,D]]
    RIGHT = [[D,-D,D], [D,-D,-D], [D,D,-D], [D,D,D]] 
    UP = [[D,D,D], [D,D,-D], [-D,D,-D], [-D,D,D]]
    DOWN = [[-D,-D,-D], [D,-D,-D], [D,-D,D], [-D,-D,D]]
    
    def draw(self, camera, projection):
        for quad in self.skyboxquads:
            quad.draw(camera, projection)
    
    def __init__(self, path, ext):
        D = Skybox.D
        self.bb = [[-D,-D,-D],[D,D,D]]
        self.skyboxquads = []
        self.skyboxquads.append(TexturedQuad(path+'skybox_front'+ext, Skybox.FRONT))
        self.skyboxquads.append(TexturedQuad(path+'skybox_back'+ext, Skybox.BACK))
        self.skyboxquads.append(TexturedQuad(path+'skybox_left'+ext, Skybox.LEFT))
        self.skyboxquads.append(TexturedQuad(path+'skybox_right'+ext, Skybox.RIGHT))
        self.skyboxquads.append(TexturedQuad(path+'skybox_up'+ext, Skybox.UP))
        self.skyboxquads.append(TexturedQuad(path+'skybox_down'+ext, Skybox.DOWN))

class Scene(object):
    def __init__(self, fov, aspect):
        self.skybox = None
        self.helicopter = None
        self.simpleObjects = []
        self.cameras = []
        self.cameracycle = None
        self.skyboxes = []
        self. skycycle = None
        self.updateProjection(fov, aspect)
        
    def addCamera(self, cam_type, *information):
        if cam_type == CameraType.FIX:
            camera = FixCamera(*information)
        if cam_type == CameraType.FOLLOW:
            camera = FollowCamera(*information)
        if cam_type == CameraType.THIRD_PERSON:
            camera = ThirdPersonCamera(*information)
        self.cameras.append(camera)

    def addHelicopter(self, helicopter_info, position=None):
        self.helicopter = Heli(*helicopter_info)
        if position:
            self.helicopter.position = position
            
    def addSimpleObject(self, obj_info):
        simpleObj = SimpleObjObject(*obj_info)
        self.simpleObjects.append(simpleObj)

    def addSkybox(self, skybox_info):
        self.skyboxes.append(Skybox(*skybox_info))

    def updateProjection(self, fov, aspect):
        self.projection = trafo.perspectiveMatrix(fov, aspect, 0.1, 1000.1)

    def switchCam(self):
        self.camera = next(self.cameracycle)

    def switchSky(self):
        self.skybox = next(self.skycycle)
        
    def _heliIntersectSkybox(self):
        heli_center = self.helicopter.position

        intersectX_right = False if heli_center[0] < 0 else True
        intersectY_top = False if heli_center[1] < 0 else True
        intersectZ_front = False if heli_center[2] < 0 else True
        
        bb = self.skybox.bb
        #both are lists like [x,y,z]
        curr_min_dist_to_object = [min(abs(x[0] - x[1]), abs(x[0] - x[2])) for x in zip(heli_center, bb[0],bb[1])]
        min_allowed_dist = self.helicopter.bb[1]

        intersectX = curr_min_dist_to_object[0] <= min_allowed_dist[0]
        intersectY = curr_min_dist_to_object[1] <= min_allowed_dist[1]
        intersectZ = curr_min_dist_to_object[2] <= min_allowed_dist[2]
        return [[intersectX, intersectX_right],[intersectY, intersectY_top],[intersectZ, intersectZ_front]]

    def _checkXIntersection(self, intersect_data):
        intersectsX = intersect_data[0][0]
        intersectX_right = intersect_data[0][1]
        if intersectsX:
            if intersectX_right:
                self.helicopter.can_move_right = False
            else:
                self.helicopter.can_move_left = False
        else:
            self.helicopter.can_move_right = True
            self.helicopter.can_move_left = True

    def _checkYIntersection(self, intersect_data):
        intersectsY = intersect_data[1][0]
        intersectY_top = intersect_data[1][1]
        if intersectsY:
            if intersectY_top:
                self.helicopter.can_move_up = False
            else:
                self.helicopter.can_move_down = False
        else:
            self.helicopter.can_move_up = True
            self.helicopter.can_move_down = True

    def _checkZIntersection(self, intersect_data):
        intersectsZ = intersect_data[2][0]
        intersectY_front = intersect_data[2][1]
        if intersectsZ:
            if intersectY_front:
                self.helicopter.can_move_forward = False
            else:
                self.helicopter.can_move_backward = False
        else:
            self.helicopter.can_move_forward = True
            self.helicopter.can_move_backward = True 

    def updateHeliIntersections(self):
        intersect_data = self._heliIntersectSkybox()
        self._checkXIntersection(intersect_data)
        self._checkYIntersection(intersect_data)
        self._checkZIntersection(intersect_data)

    def draw(self):
        if not self.cameracycle:
            self.cameracycle = itertools.cycle(self.cameras)
            self.camera = next(self.cameracycle)

        if not self.skycycle:
            self.skycycle = itertools.cycle(self.skyboxes)
            self.skybox = next(self.skycycle)

        if self.skybox:
            self.skybox.draw(self.camera, self.projection)
        if self.helicopter:
            self.updateHeliIntersections()
            self.helicopter.draw(self.camera, self.projection)
        for simpleObj in self.simpleObjects:
            simpleObj.draw(self.camera, self.projection)

    
        
        
