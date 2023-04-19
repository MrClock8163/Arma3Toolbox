import bpy
import bmesh
import struct
import math
import re
import time
import os
import mathutils
from mathutils import Vector
from . import binary_handler as binary
from ..utilities import lod as lodutils
from ..utilities import proxy as proxyutils
from ..utilities import structure as structutils
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
    
def read_vertex(file): # flags can be dumped
    x,y,z,flag = struct.unpack('<fffI',file.read(16))
    return x,z,y,flag
    
def read_normal(file):
    x,y,z = struct.unpack('<fff',file.read(12))
    return -x,-z,-y
    
def read_pseudo_vertextable(file): # UV can be dumped because they are read from the TAGGs anyway
    pointID, normalID, U, V = struct.unpack('<IIff',file.read(16))
    
    return pointID,normalID,U,V
    
def read_face(file):
    numSides = binary.readULong(file)
    
    vertTables = [] # should instead return the individual lists to avoid unecessary data
    for i in range(numSides):        
        vertTables.append(read_pseudo_vertextable(file))
    
    if numSides < 4:
        read_pseudo_vertextable(file)
        
    flags = binary.readULong(file) # flags can be dumped
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
        
def process_TAGGs(file,bm,additionalData,numPoints,numFaces):

    namedSelections = []
    properties = {}
    while True:
        # taggActive = binary.readBool(file)
        file.read(1)
        taggName = binary.readAsciiz(file)
        taggLength = binary.readULong(file)
        
        # print(taggName,taggLength)
        
        # EOF
        if taggName == "#EndOfFile#":
            if taggLength != 0:
                raise IOError("Invalid EOF")
            break
            
        # Sharps (technically redundant with the split vertex normals, may be scrapped later)
        elif taggName == "#SharpEdges#":
            for i in range(int(taggLength / (4 * 2))):
                point1ID = binary.readULong(file)
                point2ID = binary.readULong(file)
                
                if point1ID != point2ID:
                    edge = bm.edges.get([bm.verts[point1ID],bm.verts[point2ID]])
                    
                    if edge is not None:
                        edge.smooth = False
        
        # Property
        elif taggName == "#Property#" and 'PROPS' in additionalData:
            if taggLength != 128:
                raise IOError(f"Invalid named property length: {taggLength}")
                
            key = binary.readChar(file,64)
            value = binary.readChar(file,64)
            
            if key not in properties:
                properties[key] = value
        
        # Mass
        elif taggName == "#Mass#" and 'MASS' in additionalData:
            massLayer = bm.verts.layers.float.new("a3ob_mass") # create new BMesh layer to store mass data
            for i in range(numPoints):
                mass = binary.readFloat(file)
                bm.verts[i][massLayer] = mass
            
        # UV
        elif taggName == "#UVSet#" and 'UV' in additionalData:
            UVID = binary.readULong(file)
            UVlayer = bm.loops.layers.uv.new(f"UVSet {UVID}")
            
            for face in bm.faces:
                for loop in face.loops:
                    loop[UVlayer].uv = (binary.readFloat(file),1-binary.readFloat(file))
            
            
        # Named selections
        elif not re.match("#.*#",taggName) and 'SELECTIONS' in additionalData:
            namedSelections.append(taggName)
            bm.verts.layers.deform.verify()
            deform = bm.verts.layers.deform.active
            
            for i in range(numPoints):
                b = binary.readByte(file)
                weight = decode_selectionWeight(b)
                if b != 0:
                    bm.verts[i][deform][len(namedSelections)-1] = weight
                
            file.read(numFaces) # dump face selection data
            
        else:
            file.read(taggLength) # dump all other TAGGs
            
    return namedSelections, properties
    
def process_materials(objData,faceDataDict,materialDict):
    blenderMatIndices = {} # needed because otherwise materials and textures with same names, but in different folders may cause issues
    proceduralStringPattern = "#\(.*?\)\w+\(.*?\)"
    colorStringPattern = "#\(\s*argb\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)color\(\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,([a-zA-Z]+)\)"
    
    for i in range(len(faceDataDict)):
        faceData = faceDataDict[i]
    
        textureName = faceData[2].strip()
        materialName = faceData[3].strip()
        
        blenderMat = None
        
        if (textureName,materialName) in materialDict:
            blenderMat = materialDict[(textureName,materialName)]
            
        else:
            blenderMat = bpy.data.materials.new(f"P3D: {os.path.basename(textureName)} :: {os.path.basename(materialName)}")
            OBprops = blenderMat.a3ob_properties_material
                
            if re.match(proceduralStringPattern,textureName):
                tex = re.match(colorStringPattern,textureName)
                if tex:
                    OBprops.textureType = 'COLOR'
                    groups = tex.groups()
                    
                    try:
                        OBprops.colorType = groups[4].upper()
                        OBprops.colorValue = (float(groups[0]),float(groups[1]),float(groups[2]),float(groups[3]))
                    except:
                        OBprops.textureType = 'CUSTOM'
                        OBprops.colorString = textureName
                        
                else:
                    OBprops.textureType = 'CUSTOM'
                    OBprops.colorString = textureName
            else:
                OBprops.texturePath = textureName
            
            OBprops.materialPath = materialName
            materialDict[(textureName,materialName)] = blenderMat
            
        if blenderMat.name not in objData.materials:
            objData.materials.append(blenderMat)
            blenderMatIndices[blenderMat] = len(objData.materials)-1

        matIndex = blenderMatIndices[blenderMat]
            
        objData.polygons[i].material_index = matIndex
        
    return materialDict
    
def process_normals(objData,faceDataDict,normalsDict):
    loopNormals = []
    for face in objData.polygons:
        vertTables = faceDataDict[face.index][0]
        
        for i in face.loop_indices:
            loop = objData.loops[i]
            vertID = loop.vertex_index
            
            for vertTable in vertTables:
                if vertTable[0] == vertID:
                    loopNormals.insert(i,normalsDict[vertTable[1]])   
    
    objData.normals_split_custom_set(loopNormals)
    objData.free_normals_split()
        
def group_LODs(LODs,groupBy = 'TYPE'):    
    collections = {}
    
    groupDict = data.LODgroups[groupBy]
    
    for lodObj,res in LODs:
        lodIndex, lodRes = lodutils.getLODid(res)
        groupName = groupDict[lodIndex]
        
        if groupName not in collections.keys():
            collections[groupName] = bpy.data.collections.new(name=groupName)
            
        collections[groupName].objects.link(lodObj)
            
    return collections
    
def read_LOD(context,file,materialDict,additionalData):
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
    
    
    # Read point table    
    timePOINTstart = time.time()
    points = []
    for i in range(numPoints):
        newPoint = read_vertex(file)
        points.append(newPoint[:-1])
        
    print(f"Points took {time.time()-timePOINTstart}")
    
    print(f"Points: {numPoints}")
    
    # Read face normals
    normalsDict = {}
    for i in range(numNormals):
        normalsDict[i] = read_normal(file)
    
    print(f"Normals: {numNormals}")
    
    # Read faces
    faces = []
    faceDataDict = {}
    timeFACEstart = time.time()
    for i in range(numFaces):
        newFace = read_face(file)
        faces.append([i[0] for i in newFace[0]])
        faceDataDict[i] = newFace
        
    objData = bpy.data.meshes.new("Temp LOD")
    objData.from_pydata(points,[],faces)
    objData.update(calc_edges=True)
    
    for face in objData.polygons:
        face.use_smooth = True
        
    bm = bmesh.new()
    bm.from_mesh(objData)
    
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    print(f"Faces took {time.time()-timeFACEstart}")
    
    print(f"Faces: {numFaces}")
    
    # Read TAGGs 
    taggSignature = read_signature(file)
    if taggSignature != "TAGG":
        raise IOError(f"Invalid TAGG section signature: {taggSignature}")
    
    namedSelections, properties = process_TAGGs(file,bm,additionalData,numPoints,numFaces)
            
    LODresolution = binary.readFloat(file)
    
    # print(LODresolution)
    
    lodIndex, lodRes = lodutils.getLODid(LODresolution)
    lodName = lodutils.formatLODname(lodIndex,lodRes)
    print(lodName)
        
    objData.use_auto_smooth = True
    objData.auto_smooth_angle = math.radians(180)
    objData.name = lodName
    obj = bpy.data.objects.new(lodName,objData)
    
    # Setup LOD property
    OBprops = obj.a3ob_properties_object
    
    OBprops.isArma3LOD = True
    try:
        OBprops.LOD = str(lodIndex)
    except:
        OBprops.LOD = "30"
        
    OBprops.resolution = lodRes
    
    # Add named properties
    for key in properties:
        item = OBprops.properties.add()
        item.name = key
        item.value = properties[key]
        
    bm.normal_update()
    bm.to_mesh(objData)
    bm.free()
    
    # Create materials
    if 'MATERIALS' in additionalData:
        materialDict = process_materials(objData,faceDataDict,materialDict)
        
    
    # Apply split normals
    if 'NORMALS' in additionalData and lodIndex in data.LODvisuals: 
        process_normals(objData,faceDataDict,normalsDict)
        
    # Named selections
    for name in namedSelections:
        obj.vertex_groups.new(name=name)
    
    print(f"LOD overall took {time.time()-timeP3Dstart}")
    
    return obj, LODresolution, materialDict
    
def import_file(operator,context,file):
    timeFILEstart = time.time()

    additionalData = set()
    
    if operator.allowAdditionalData:
        additionalData = operator.additionalData
    
    version, LODcount = read_header(file)
    
    print(f"File version: {version}")
    print(f"Number of LODs: {LODcount}")
    
    
    if version != 257:
        raise IOError(f"Unsupported file version: {version}")
    
    LODs = []
    groups = []
    
    materialDict = None
    if 'MATERIALS' in additionalData:
        materialDict = {
            ("",""): bpy.data.materials.get("P3D: no material",bpy.data.materials.new("P3D: no material"))
        }
    
    # for i in range(1):
    for i in range(LODcount):
        lodObj, res, materialDict = read_LOD(context,file,materialDict,additionalData)
        
        if operator.validateMeshes:
            lodObj.data.validate(clean_customdata=False)
        
        LODs.append((lodObj,res))
        
    rootCollection = bpy.context.scene.collection
    
    if operator.enclose:
        rootCollection = bpy.data.collections.new(name=os.path.basename(operator.filepath))
        bpy.context.scene.collection.children.link(rootCollection)       
    
    if operator.groupby == 'NONE':
        for item in LODs:
            rootCollection.objects.link(item[0])
        return # NOT GOOD BECAUSE IT HALTS EVERY OTHER OPERATION
        
    colls = group_LODs(LODs,operator.groupby)
        
    for group in colls.values():
        rootCollection.children.link(group)
        
    # Set up proxies
    # For later reference: https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object
    if operator.proxyHandling != 'NOTHING' and 'SELECTIONS' in additionalData:
        selectionPattern = "proxy:(.*)\.(\d{3})"
        for data in LODs:
            LOD = data[0]
                
            bpy.context.view_layer.objects.active = LOD
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            
            for group in LOD.vertex_groups:
                selection = group.name
                proxy = re.match(selectionPattern,selection)
                if not proxy:
                    continue
                    
                LOD.vertex_groups.active_index = LOD.vertex_groups.get(selection).index
                
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.separate(type='SELECTED')
                
            bpy.ops.object.mode_set(mode='OBJECT')
            
            proxyObjects = [proxy for proxy in bpy.context.selected_objects if proxy != LOD]
            
            if operator.proxyHandling == 'CLEAR':
                bpy.ops.object.delete({"selected_objects": proxyObjects})
                
            elif operator.proxyHandling == 'SEPARATE':
                for obj in proxyObjects:
                    
                    rotate = proxyutils.getTransformRot(obj)
                    obj.data.transform(rotate)
                    obj.matrix_world = rotate.inverted()
                    obj.a3ob_properties_object_proxy.isArma3Proxy = True
                    
                    translate = mathutils.Matrix.Translation(-obj.data.vertices[proxyutils.findCenterIndex(obj.data)].co)
                    
                    obj.data.transform(translate)
                    
                    obj.matrix_world @= translate.inverted()
                    
                    structutils.cleanupVertexGroups(obj)
                    
                    for vgroup in obj.vertex_groups:
                        proxyData = re.match(selectionPattern,vgroup.name)
                        if proxyData:
                            obj.vertex_groups.remove(vgroup)
                            proxyDataGroups = proxyData.groups()
                            obj.a3ob_properties_object_proxy.proxyPath = proxyDataGroups[0]
                            obj.a3ob_properties_object_proxy.proxyIndex = int(proxyDataGroups[1])
                    
                    obj.data.materials.clear()
                    obj.data.materials.append(materialDict[("","")])
                    
                    obj.parent = LOD
                    
                    
                    
            bpy.ops.object.select_all(action='DESELECT')
            
        
    print(f"File took {time.time()-timeFILEstart}")
    