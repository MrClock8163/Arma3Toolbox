import bpy
import bmesh
import struct
import math
import re
import time
from mathutils import Vector
from . import binary_handler as binary
from .. import utility as utils
from .. import data

def read_signature(file):
    return binary.readChar(file,4)

def read_header(file):
    signature = read_signature(file)
    print(f"Header signature: {signature}")
    if signature != "MLOD":
        raise IOError(f"Invalid MLOD signature: {signature}")
        
    version = binary.readULong(file)
    LODcount = binary.readULong(file)
    
    return version, LODcount
    
def read_vertex(file):
    x,y,z,flag = struct.unpack('<fffI',file.read(16))
    return x,z,y,flag
    
def read_normal(file):
    x,y,z = struct.unpack('<fff',file.read(12))
    return -x,-z,-y
    
def read_pseudo_vertextable(file):
    pointID, normalID, U, V = struct.unpack('<IIff',file.read(16))
    
    return pointID,normalID,U,V
    
def read_face(file):
    numSides = binary.readULong(file)
    
    vertTables = []
    for i in range(numSides):        
        vertTables.append(read_pseudo_vertextable(file))
    
    if numSides < 4:
        read_pseudo_vertextable(file)
        
    flags = binary.readULong(file)
    texture = binary.readAsciiz(file)
    material = binary.readAsciiz(file)
    
    return vertTables,flags,texture,material
    
def decode_selectionWeight(b):
    if b == 0:
        return 0.0
    elif b == 2:
        return 1.0
    elif b > 2:
        return 1.0 - round((b-2)/2.55555)*0.01
    elif b < 0:
        return -round(b/2.55555)*0.01
    else:
        return 1.0 # ¯\_(ツ)_/¯
        
def group_LODs(LODs,groupBy = 'TYPE'):    
    collections = {}
    
    groupDict = data.LODgroups[groupBy]
    
    for lodObj,res in LODs:
            lodIndex, lodRes = utils.getLODid(res)
            groupName = groupDict[lodIndex]
            
            if groupName not in collections.keys():
                collections[groupName] = bpy.data.collections.new(name=groupName)
                
            collections[groupName].objects.link(lodObj)
            
    return collections
    
def read_LOD(context,file,preserveNormals):
    timeP3Dstart = time.time()

    # Read LOD header
    signature = read_signature(file)
    if signature != "P3DM":
        raise IOError(f"Unsupported LOD signature: {signature}")
        
    versionMajor = binary.readULong(file)
    versionMinor = binary.readULong(file)
    
    if versionMajor != 0x1c or versionMinor != 0x100:
        raise IOError(f"Unsupported LOD version: {versionMajor}.{versionMinor}")
        
    numPoints = binary.readULong(file)
    numNormals = binary.readULong(file)
    numFaces = binary.readULong(file)
    
    flags = binary.readULong(file)
    
    bm = bmesh.new()
    
    # Read point table    
    timePOINTstart = time.time()
    for i in range(numPoints):
        bm.verts.new(read_vertex(file)[:-1])
        
    bm.verts.ensure_lookup_table()
    print(f"Points took {time.time()-timePOINTstart}")
    
    print(f"Points: {numPoints}")
    
    # Read face normals
    normalsDict = {}
    for i in range(numNormals):
        normalsDict[i] = read_normal(file)
    
    print(f"Normals: {numNormals}")
    
    # Read faces
    faceDataDict = {}
    timeFACEstart = time.time()
    for i in range(numFaces):
        newFace = read_face(file)
        bm.faces.new([bm.verts[i[0]] for i in newFace[0]]).smooth = True
        faceDataDict[i] = newFace
        
        
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"Faces took {time.time()-timeFACEstart}")
    
    print(f"Faces: {numFaces}")
    
    # Read TAGGs 
    taggSignature = read_signature(file)
    if taggSignature != "TAGG":
        raise IOError(f"Invalid TAGG section signature: {taggSignature}")
    
    # taggs = []
    namedSelections = []
    while True:
        taggActive = binary.readBool(file)
        taggName = binary.readAsciiz(file)
        taggLength = binary.readULong(file)
        
        print(taggName)
        
        # EOF
        # masses = []
        properties = {}
        if taggName == "#EndOfFile#":
            if taggLength != 0:
                raise IOError("Invalid EOF")
            break
            
        # Sharps (technically redundant with the split vertex normals, may be scrapped later)
        elif taggName == "#SharpEdges#":
            for i in range(int(taggLength / (4 * 2))):
                point1ID = binary.readULong(file)
                point2ID = binary.readULong(file)
                
                edge = bm.edges.get([bm.verts[point1ID],bm.verts[point2ID]])
                
                if edge is not None:
                    edge.smooth = False
        
        # Property
        elif taggName == "#Property#":
            if taggLength != 128:
                raise IOError(f"Invalid named property length: {taggLength}")
            key = binary.readChar(file,64)
            value = binary.readChar(file,64)
            properties[key] = value
            
            # IMPLEMENT HANDLING!!!
        
        # Mass
        elif taggName == "#Mass#":
            massLayer = bm.verts.layers.float.new("a3ob_mass") # create new BMesh layer to store mass data
            for i in range(numPoints):
                mass = binary.readFloat(file)
                # print(mass)
                # masses.append(mass)
                bm.verts[i][massLayer] = mass
                # vertsDict[i][massLayer] = mass
            
        # UV
        elif taggName == "#UVSet#":
            UVID = binary.readULong(file)
            UVlayer = bm.loops.layers.uv.new(f"UVSet {UVID}")
            
            for face in bm.faces:
                for loop in face.loops:
                    loop[UVlayer].uv = (binary.readFloat(file),1-binary.readFloat(file))
            
            
        # Named selections
        elif not re.match("#.*#",taggName):
            namedSelections.append(taggName)
            bm.verts.layers.deform.verify()
            deform = bm.verts.layers.deform.active
            
            for i in range(numPoints):
                b = binary.readByte(file)
                weight = decode_selectionWeight(b)
                if b != 0:
                    bm.verts[i][deform][len(namedSelections)-1] = weight
                
            binary.readBytes(file,numFaces)
            
        else:
            binary.readBytes(file,taggLength) # dump all other TAGGs
            
    LODresolution = binary.readFloat(file)
    
    print(LODresolution)
    
    lodIndex, lodRes = utils.getLODid(LODresolution)
    lodName = utils.formatLODname(lodIndex,lodRes)
    print(lodName)
        
    objData = bpy.data.meshes.new(lodName)
    objData.use_auto_smooth = True
    objData.auto_smooth_angle = math.radians(180)
    obj = bpy.data.objects.new(lodName,objData)
    
    for name in namedSelections:
        obj.vertex_groups.new(name=name)
        
    bm.normal_update()
    bm.to_mesh(objData)
    bm.free()
    
    # Apply split normals
    if preserveNormals and lodIndex in data.LODvisuals: 
        
        loopNormals = []
        for face in objData.polygons:
            vertTables = faceDataDict[face.index][0]
            
            for i in face.loop_indices:
                loop = objData.loops[i]
                vertID = loop.vertex_index
                
                for vertTable in vertTables:
                    if vertTable[0] == vertID:
                        loopNormals.insert(i,normalsDict[vertTable[1]])   
        
        objData.validate(clean_customdata=False)
        objData.normals_split_custom_set(loopNormals)
        objData.free_normals_split()
    
    print(f"LOD overall took {time.time()-timeP3Dstart}")
    
    return obj, LODresolution
    
def import_file(context,file,groupBy,preserveNormals,encloseIn = ""):
    
    timeFILEstart = time.time()
    
    version, LODcount = read_header(file)
    
    print(f"File version: {version}")
    print(f"Number of LODs: {LODcount}")
    
    
    if version != 257:
        raise IOError(f"Unsupported file version: {version}")
    
    LODs = []
    groups = []
    
    for i in range(LODcount):
        lodObj, res = read_LOD(context,file,preserveNormals)
        
        LODs.append((lodObj,res))
        
    rootCollection = bpy.context.scene.collection
    
    if encloseIn != "":
        rootCollection = bpy.data.collections.new(name=encloseIn)
        bpy.context.scene.collection.children.link(rootCollection)       
    
    if groupBy == 'NONE':
        for item in LODs:
            rootCollection.objects.link(item[0])
        return
        
    colls = group_LODs(LODs,groupBy)

        
        
    for group in colls.values():
        rootCollection.children.link(group)
        
    print(f"File took {time.time()-timeFILEstart}")
    