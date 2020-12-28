# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GL.shaders import *

from numpy import *
from math import *

class Sender(object):
    def __init__(self, shaderprogram, varnames):
        self.locations = {}
        for varname in varnames:
            self.locations[varname] = glGetUniformLocation(shaderprogram, varname)

    def _getloc(self, varname):
        return self.locations[varname]

    def sendMat4(self, varname, matrix):
        glUniformMatrix4fv(self._getloc(varname), 1, GL_TRUE, matrix.tolist())

    def sendMat3(self, varname, matrix):
        glUniformMatrix3fv(self._getloc(varname), 1, GL_TRUE, matrix.tolist())

    def sendVec4(self, varname, value):
        glUniform4f(self._getloc(varname), *value)

    def sendVec3(self, varname, value):
        glUniform3f(self._getloc(varname), *value)

    def sendValue(self, varname, value):
        glUniform1f(self._getloc(varname), value)
        
