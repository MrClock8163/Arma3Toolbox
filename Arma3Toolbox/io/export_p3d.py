import bpy
import bmesh
import os
import struct
import math
import mathutils
from . import binary_handler as binary
from ..utilities import lod as lodutils
from ..utilities import proxy as proxyutils
from ..utilities import structure as structutils
from ..utilities import data
from ..utilities.logger import ProcessLogger

def get_LOD_objects(operator,context):

    scene = context.scene
    exportObjects = scene.objects
    
    if operator.use_selection:
        exportObjects = context.selected_objects
    
    LODs = []
    for obj in exportObjects:
        if obj.type =='MESH' and obj.a3ob_properties_object.isArma3LOD and obj.a3ob_properties_object.LOD != '30':
            
            if operator.apply_modifiers:
                LODs.append(obj.evaluated_get(context.evaluated_depsgraph_get()))
            else:
                LODs.append(obj)
    
    return LODs
    
def get_resolution(obj):
    OBprops = obj.a3ob_properties_object
    
    # index,res = data.LODtypeIndex.values().index(int(OBprops.LOD))
    
    return lodutils.getLODvalue(int(OBprops.LOD),OBprops.resolution)

def encode_selectionWeight(weight):
    if weight == 0:
        return 0
        
    elif weight  == 1:
        return 1
    
    value = round(256 - 255 * weight)
    
    if value == 256:
        return 0
        
    return value

def write_vertex(file,co):
    file.write(struct.pack('<fff',co[0],co[2],co[1]))
    binary.writeULong(file,0)
    
def write_normal(file,normal):
    file.write(struct.pack('<fff',-normal[0],-normal[2],-normal[1]))

def write_pseudo_vertextable(file,loop):
    binary.writeULong(file,loop.vert.index)
    binary.writeULong(file,loop.index)
    file.write(struct.pack('<ff',0,0))

def write_face(file,bm,face):
    numSides = len(face.loops)
    binary.writeULong(file,numSides)
    
    for i in range(numSides):
        write_pseudo_vertextable(file,face.loops[i])
        
    if numSides < 4:
        file.write(struct.pack('<IIff',0,0,0,0))
    
    binary.writeULong(file,0) # face flags
    binary.writeAsciiz(file,"") # texture
    binary.writeAsciiz(file,"") # material
    
def write_sharps(file,bm):
    binary.writeByte(file,1)
    binary.writeAsciiz(file,"#SharpEdges#")
    dataSizePos = file.tell()
    binary.writeULong(file,0) # temporary placeholder value
    
    flatFaceEdges = set()
    for face in bm.faces:
        if not face.smooth:
            flatFaceEdges.update({edge for edge in face.edges})
    
    for edge in bm.edges:
        if not edge.smooth or edge in flatFaceEdges:
            file.write(struct.pack('<II',edge.verts[0].index,edge.verts[1].index))

    dataEndPos = file.tell()
    file.seek(dataSizePos,0)
    binary.writeULong(file,dataEndPos-dataSizePos-4) # fill in length data
    file.seek(dataEndPos,0)

def write_uv_set(file,bm,layer,index):
    binary.writeByte(file,1)
    binary.writeAsciiz(file,"#UVSet#")
    dataSizePos = file.tell()
    binary.writeULong(file,0) # temporary placeholder value
    binary.writeULong(file,index)
    
    for face in bm.faces:
        for loop in face.loops:
            file.write(struct.pack('<ff',loop[layer].uv[0],1-loop[layer].uv[1]))
        
    dataEndPos = file.tell()
    file.seek(dataSizePos,0)
    binary.writeULong(file,dataEndPos-dataSizePos-4) # fill in length data
    file.seek(dataEndPos,0)

def write_uv(file,bm):
    index = 0
    for layer in bm.loops.layers.uv.values():
        write_uv_set(file,bm,layer,index)
        index += 1

def write_mass(file,bm,numVerts):
    layer = bm.verts.layers.float.get('a3ob_mass')
    if not layer:
        return
        
    binary.writeByte(file,1)
    binary.writeAsciiz(file,"#Mass#")
        
    binary.writeULong(file,numVerts*4)
    
    for vertex in bm.verts:
        binary.writeFloat(file,vertex[layer])
        
def write_vertex_group(file,bm,layer,name,index):
    binary.writeByte(file,1)
    binary.writeAsciiz(file,name)
    dataSizePos = file.tell()
    binary.writeULong(file,0) # temporary placeholder value
    
    for vert in bm.verts:
        value = vert[layer].get(index,0)
        print(encode_selectionWeight(value))
        binary.writeByte(file,encode_selectionWeight(value))
        
    for face in bm.faces:
        weight = sum([vert[layer].get(index,0) for vert in face.verts])
        if round(weight,2) == len(face.verts):
            binary.writeByte(file,1)
        else:
            binary.writeByte(file,0) # need to figure out how to detect selected faces
    
    dataEndPos = file.tell()
    file.seek(dataSizePos,0)
    binary.writeULong(file,dataEndPos-dataSizePos-4) # fill in length data
    file.seek(dataEndPos,0)

def write_selections(file,bm,names):
    if len(names) == 0:
        return
    
    layer = bm.verts.layers.deform.active
    
    for i,name in enumerate(names):
        write_vertex_group(file,bm,layer,name,i)
    
def write_property(file,key,value):
    binary.writeByte(file,1)
    binary.writeAsciiz(file,"#Property#")
    binary.writeULong(file,128)
    file.write(struct.pack('<64s',key.encode('ASCII')))
    file.write(struct.pack('<64s',value.encode('ASCII')))
    
def write_named_properties(file,obj):
    OBprops = obj.a3ob_properties_object
    
    writtenProps = set()
    for prop in OBprops.properties:
        if prop.name not in writtenProps:
            writtenProps.add(prop.name)
            write_property(file,prop.name,prop.value)

def write_header(file,LODcount):
    binary.writeChars(file,'MLOD')
    binary.writeULong(file,257)
    binary.writeULong(file,LODcount)
    
def write_LOD(file,obj):
    binary.writeChars(file,'P3DM')
    binary.writeULong(file,0x1c)
    binary.writeULong(file,0x100)
    
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
        
    mesh = obj.data.copy()
    mesh.calc_normals_split()
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    numVerts = len(mesh.vertices)
    numLoops = len(mesh.loops)
    numFaces = len(mesh.polygons)
    
    binary.writeULong(file,numVerts)
    binary.writeULong(file,numLoops) # number of normals
    binary.writeULong(file,numFaces)
    
    binary.writeULong(file,0) # unknown flags/padding
    
    for vert in bm.verts:
        write_vertex(file,vert.co)
        
    for loop in mesh.loops:
        write_normal(file,loop.normal)
        
    for face in bm.faces:
        write_face(file,bm,face)
        
    binary.writeChars(file,'TAGG') # TAGG section start
        
    write_sharps(file,bm)
    write_uv(file,bm)
    
    if obj.a3ob_properties_object.LOD == '6':
        write_mass(file,bm,numVerts) # need to make sure to only export for Geo LODs
        
    
    write_named_properties(file,obj)
    write_selections(file,bm,[group.name for group in obj.vertex_groups])
    
    binary.writeByte(file,1)
    binary.writeAsciiz(file,"#EndOfFile#") # EOF signature
    binary.writeULong(file,0)
    
    binary.writeFloat(file,get_resolution(obj)) # LOD resolution index
    
    bm.free()

def export_file(operator,context,file):
    logger = ProcessLogger()
    
    LODobjects = get_LOD_objects(operator,context)
    
    print(LODobjects)
    
    LODcount = len(LODobjects)
    
    write_header(file,LODcount)
    
    for obj in LODobjects:
        write_LOD(file,obj)