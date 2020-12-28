# -*- coding: utf-8 -*-
import sys, os

from OpenGL.arrays import vbo
from numpy import *
from math import *

FLOAT_INF = float('inf')
        
class ReadObj(object):
    def __init__(self, path, filename, groupindices=None):

        filex = open(path+filename)
        
        self.vertices = []
        self.tex_coords = []
        self.normals = []
        self.materials = {}
        self.face_groups = {}
        self.scale = 0
        self.center = []
        
        self._read_obj(path, filex)
        
        
    def _read_obj(self, path, filex):
        curr_face_group = None

        for line in filex:
            splittedline = line.split()
            if not splittedline: continue #empty line
            
            key = splittedline[0]
            parts = splittedline[1:]

            if key == '#': continue #comment
                    
            elif key == 'mtllib':
                mtl_filename = parts[0].split('/')[-1]
                self._read_mtllib(path, mtl_filename)

            elif key == 'v':
                vertex = [float(part) for part in parts]
                self.vertices.append(vertex)
            
            elif key == 'vt':
                tex_coord = [float(part) for part in parts]
                self.tex_coords.append(tex_coord)

            elif key == 'vn':
                normal = [float(part) for part in parts]
                self.normals.append(normal)

            elif key == 'usemtl':
                material_name = parts[0]
                curr_face_group = FaceGroup()
                curr_face_group.material_name = material_name
                if material_name not in self.face_groups:
                    self.face_groups[material_name] = curr_face_group
                else:
                    curr_face_group = self.face_groups[material_name]
                    
            elif key == 'f':
                if len(parts) == 4: # Quad to Triangles
                    triangle_1 = parts[:3] 
                    triangle_2 = parts[:-3]+parts[2:]
                    self._parse_face(triangle_1, curr_face_group)
                    self._parse_face(triangle_2, curr_face_group)
                elif len(parts) == 3:
                    self._parse_face(parts, curr_face_group)
        self._to_canonview()

        
    def _to_canonview(self):
        bb = [list(map(min, list(zip(*self.vertices)))), list(map(max, list(zip(*self.vertices))))]
        scale = 2.0 / max([(x[1] - x[0]) for x in zip(*bb)])
        self.center = [(x[0]+x[1]) / 2.0 * scale  for x in zip(*bb)]
        self.vertices = [[p[0] * scale - self.center[0], p[1] * scale - self.center[1], p[2] * scale - self.center[2]] for p in self.vertices]
        self.bb = [[p[0] * scale - self.center[0], p[1] * scale - self.center[1], p[2] * scale - self.center[2]] for p in bb]
    def _read_mtllib(self, path, filename):
        # MTL vgl http://paulbourke.net/dataformats/mtl/        
        filex = open(path + filename)

        for line in filex:
            splittedline = line.split()
            if not splittedline: continue #empty line

            key = splittedline[0]
            parts = splittedline[1:]

            if key == '#': continue #comment

            elif key == 'newmtl':
                material = Material()
                material.name = parts[0]
                self.materials[parts[0]] = material
            
            elif key == 'Ka':
                material.ambient = [float(part) for part in parts]
            
            elif key == 'Kd':
                material.diffuse = [float(part) for part in parts]
            
            elif key == 'Ks':
                material.specular = [float(part) for part in parts]
            
            elif key == 'd':  
                material.ambient += [float(parts[0])]
                material.diffuse += [float(parts[0])]
                material.specular += [float(parts[0])]
                material.alpha = float(parts[0])
            
            elif key == 'Ns':
                material.exponent = float(parts[0])
            
            elif key == 'illum': 
                continue
            
            elif key == 'map_Kd':
                material.texture_filename = path+parts[0]
                
    def _parse_face(self, parts, curr_face_group):
        for part in parts:
            vertex_i, texture_i, normal_i = part.split('/')
            indices = [int(vertex_i)-1, int(texture_i)-1, int(normal_i)-1]
            curr_face_group.indices.append(indices)
            
class SimpleObjData(object):
    def __init__(self, obj):
        self.vertices = obj.vertices
        self.tex_coords = obj.tex_coords
        self.normals = obj.normals
        self.face_groups = obj.face_groups                    
        self.materials = obj.materials
        self.vbo_dic = {}
        
        self._initGeometry()

    def _initGeometry(self):       
        bb = [list(map(min, list(zip(*self.vertices)))), list(map(max, list(zip(*self.vertices))))]
        self.center = [(x[0]+x[1]) / 2.0  for x in zip(*bb)]
        self._create_vbos()

    def _create_vbos(self):
        for face_group in self.face_groups.values():
            vboo = face_group.create_vbo(self.vertices, self.tex_coords, self.normals, 0, FLOAT_INF)
            self.vbo_dic[face_group.material_name] = vboo
            
    def getVBO(self, materialname):
        return self.vbo_dic[materialname]
    
class MaterialData(object):
    def __init__(self, obj, materialList, minindex=0, maxindex=FLOAT_INF):
        self.vertices = []
        self.heli_vertices = obj.vertices
        self.tex_coords = obj.tex_coords
        self.normals = obj.normals
        self.face_groups = {k:v  for k,v in obj.face_groups.items() if k in materialList}                     
        self.materials = {k:v  for k,v in obj.materials.items() if k in materialList}
        self.vbo_dic = {}
        
        self._initGeometry(minindex, maxindex)

    def _initGeometry(self, minindex, maxindex):
        #init vertices
        for face_group in self.face_groups.values():
            for indices in face_group.indices:
                if indices[0] >= minindex and indices[0] <= maxindex:
                    self.vertices.append(self.heli_vertices[indices[0]])        
        bb = [list(map(min, list(zip(*self.vertices)))), list(map(max, list(zip(*self.vertices))))]
        self.center = [(x[0]+x[1]) / 2.0  for x in zip(*bb)]

        self._create_vbos(minindex, maxindex)

    def _create_vbos(self, minindex, maxindex):
        for face_group in self.face_groups.values():
            vboo = face_group.create_vbo(self.heli_vertices, self.tex_coords, self.normals, minindex, maxindex)
            self.vbo_dic[face_group.material_name] = vboo
            
    def getVBO(self, materialname):
        return self.vbo_dic[materialname]
    
class Material(object):
    def __init__(self):
        self.name = ''
        self.texture_id = 0
        self.texture_filename = None
        self.texture_id = 0
        self.ambient = None
        self.diffuse = None
        self.specular = None
        self.exponent = None
        self.alpha = None

    def has_texture(self):
        return self.texture_id != 0


class FaceGroup(object):
    def __init__(self):
        self.indices = []
        self.material_name = ''

    def create_vbo(self, vertices, tex_coords, normals, minindex, maxindex):
        data = []
        for vi, ti, ni in self.indices:
            if vi >= minindex and vi <= maxindex:
                data.append(vertices[vi])
                data.append(tex_coords[ti])       
                data.append(normals[ni])
        return vbo.VBO(array(data,'f'))

