import bpy
import bmesh
import struct
import math
import re
import time
import os
import mathutils
from . import binary_handler as binary
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import proxy as proxyutils
from ..utilities import structure as structutils
from ..utilities import data
from ..utilities.logger import ProcessLogger

def read_signature(file):
    return binary.read_char(file,4)

def read_file_header(file):
    signature = read_signature(file)
    if signature != "MLOD":
        raise IOError(f"Invalid MLOD signature: {signature}")
        
    version = binary.read_ulong(file)
    LODcount = binary.read_ulong(file)
    
    return version, LODcount
    
def read_vertex(file):
    x,y,z = struct.unpack('<fff',file.read(12))
    file.read(4) # dump vertex flags
    return x,z,y
    
def read_normal(file):
    x,y,z = struct.unpack('<fff',file.read(12))
    return -x,-z,-y
    
def read_face_pseudo_vertextable(file):
    pointID, normalID = struct.unpack('<II',file.read(8))
    file.read(8) # dump embedded UV coordinates
    
    return pointID,normalID
    
def read_face(file):
    numSides = binary.read_ulong(file)
    
    vertTables = [read_face_pseudo_vertextable(file) for i in range(numSides)] # should instead return the individual lists to avoid unecessary data
    
    if numSides < 4:
        file.read(16) # dump null bytes
        
    file.read(4) # dump face flags
    texture = binary.read_asciiz(file)
    material = binary.read_asciiz(file)
    
    return vertTables,texture,material
    
def decode_selection_weight(weight):
    if weight == 0:
        return 0.0
        
    elif weight == 1:
        return 1.0
        
    value = (256 - weight) / 255
    
    if value > 1:
        return 0
        
    return value
    
def get_file_path(path,prefs,extension = ""):
    path = utils.replace_slashes(path.strip().lower())
    
    if not prefs.reconstructPaths:
        return path
    
    if path == "":
        return ""
    
    if os.path.splitext(path)[1].lower() != extension:
        path += extension
    
    if prefs.reconstructPaths:
        root = prefs.projectRoot.strip().lower()
        if not path.startswith(root):
            absPath = os.path.join(root,path)
            
            if os.path.exists(absPath):
                return absPath
    
    return path
        
def process_taggs(file,bm,additionalData,numPoints,numFaces,logger):
    count = 0
    namedSelections = []
    properties = {}
    while True:
        count += 1
        file.read(1)
        taggName = binary.read_asciiz(file)
        taggLength = binary.read_ulong(file)
        
        # EOF
        if taggName == "#EndOfFile#":
            if taggLength != 0:
                raise IOError("Invalid EOF")
            break
            
        # Sharps (technically redundant with the split vertex normals, may be scrapped later)
        elif taggName == "#SharpEdges#" and 'NORMALS' not in additionalData:
            for i in range(int(taggLength / (4 * 2))):
                point1ID = binary.read_ulong(file)
                point2ID = binary.read_ulong(file)
                
                if point1ID != point2ID:
                    edge = bm.edges.get([bm.verts[point1ID],bm.verts[point2ID]])
                    
                    if edge is not None:
                        edge.smooth = False
        
        # Property
        elif taggName == "#Property#" and 'PROPS' in additionalData:
            if taggLength != 128:
                raise IOError(f"Invalid named property length: {taggLength}")
                
            key = binary.read_char(file,64)
            value = binary.read_char(file,64)
            
            if key not in properties:
                properties[key] = value
        
        # Mass
        elif taggName == "#Mass#" and 'MASS' in additionalData:
            massLayer = bm.verts.layers.float.new("a3ob_mass") # create new BMesh layer to store mass data
            for i in range(numPoints):
                mass = binary.read_float(file)
                bm.verts[i][massLayer] = mass
            
        # UV
        elif taggName == "#UVSet#" and 'UV' in additionalData:
            UVID = binary.read_ulong(file)
            UVlayer = bm.loops.layers.uv.new(f"UVSet {UVID}")
            
            for face in bm.faces:
                for loop in face.loops:
                    loop[UVlayer].uv = (binary.read_float(file),1-binary.read_float(file))
            
            
        # Named selections
        elif not re.match("#.*#",taggName) and 'SELECTIONS' in additionalData:
            namedSelections.append(taggName)
            bm.verts.layers.deform.verify()
            deform = bm.verts.layers.deform.active
            
            for i in range(numPoints):
                b = binary.read_byte(file)
                weight = decode_selection_weight(b)
                if b != 0:
                    bm.verts[i][deform][len(namedSelections)-1] = weight
                
            file.read(numFaces) # dump face selection data
            
        else:
            file.read(taggLength) # dump all other TAGGs
            
    logger.step("Read TAGGs: %d" % count)
            
    return namedSelections, properties
    
def process_materials(objData,faceDataDict,materialDict,prefs):
    blenderMatIndices = {} # needed because otherwise materials and textures with same names, but in different folders may cause issues
    proceduralStringPattern = "#\(.*?\)\w+\(.*?\)"
    colorStringPattern = "#\(\s*argb\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)color\(\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,([a-zA-Z]+)\)"
    
    for i in range(len(faceDataDict)):
        faceData = faceDataDict[i]
    
        textureName = faceData[1].strip()
        materialName = faceData[2].strip()
        
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
                OBprops.texturePath = get_file_path(textureName,prefs)
            
            OBprops.materialPath = get_file_path(materialName,prefs)
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
        
def group_lods(LODs,groupBy = 'TYPE'):    
    collections = {}
    
    groupDict = data.LODgroups[groupBy]
    
    for lodObj,res,_ in LODs:
        lodIndex, lodRes = lodutils.get_lod_id(res)
        groupName = groupDict[lodIndex]
        
        if groupName not in collections:
            collections[groupName] = bpy.data.collections.new(name=groupName)
            
        collections[groupName].objects.link(lodObj)
            
    return collections
    
def build_collections(LODs,operator,rootCollection):

    if operator.enclose:
        rootCollection = bpy.data.collections.new(name=os.path.basename(operator.filepath))
        bpy.context.scene.collection.children.link(rootCollection)
    
    if operator.groupby == 'NONE':
        for item in LODs:
            rootCollection.objects.link(item[0])
    else:
        colls = group_lods(LODs,operator.groupby)
            
        for group in colls.values():
            rootCollection.children.link(group)

def transform_proxy(obj): # Align the object coordinate system with the proxy directions
    rotate = proxyutils.get_transform_rotation(obj)
    obj.data.transform(rotate)
    obj.matrix_world = rotate.inverted()
    obj.a3ob_properties_object_proxy.isArma3Proxy = True
    
    translate = mathutils.Matrix.Translation(-obj.data.vertices[proxyutils.find_center_index(obj.data)].co)
    
    obj.data.transform(translate)
    
    obj.matrix_world @= translate.inverted()

def process_proxies(LODs,operator,materialDict,prefs):
    selectionPattern = "proxy:(.*)\.(\d{3})"
    placeholderPattern = "@proxy_(\d{4})"
    
    for LOD,_,proxySelections in LODs:
        bpy.context.view_layer.objects.active = LOD
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        for group in LOD.vertex_groups:
            selection = group.name
            if not re.match(placeholderPattern,selection):
                continue
                
            LOD.vertex_groups.active = group
            
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.separate(type='SELECTED')
            LOD.vertex_groups.remove(group)
            
        bpy.ops.object.mode_set(mode='OBJECT')
        
        proxyObjects = [proxy for proxy in bpy.context.selected_objects if proxy != LOD]
        
        if operator.proxyHandling == 'CLEAR':
            bpy.ops.object.delete({"selected_objects": proxyObjects})
            
        elif operator.proxyHandling == 'SEPARATE':
            for obj in proxyObjects:
                
                transform_proxy(obj)
                structutils.cleanupVertexGroups(obj)
                
                for vgroup in obj.vertex_groups:
                    name = vgroup.name
                    
                    if name not in proxySelections:
                        continue
                        
                    proxyData = re.match(selectionPattern,proxySelections[name])
                    
                    obj.vertex_groups.remove(vgroup)
                    proxyDataGroups = proxyData.groups()
                    obj.a3ob_properties_object_proxy.proxyPath = get_file_path(proxyDataGroups[0],prefs,".p3d")
                    obj.a3ob_properties_object_proxy.proxyIndex = int(proxyDataGroups[1])
                
                obj.data.materials.clear()
                obj.data.materials.append(materialDict[("","")])
                
                obj.parent = LOD
                
        bpy.ops.object.select_all(action='DESELECT')

def read_lod(context,file,materialDict,additionalData,logger,prefs):
    logger.level_up()

    # Read LOD header
    signature = read_signature(file)
    if signature != "P3DM":
        raise IOError(f"Unsupported LOD signature: {signature}")
        
    versionMajor = binary.read_ulong(file)
    versionMinor = binary.read_ulong(file)
    
    if versionMajor != 0x1c or versionMinor != 0x100:
        raise IOError(f"Unsupported LOD version: {versionMajor}.{versionMinor}")
        
    logger.step("Type: P3DM")
    logger.step(f"Version: {versionMajor}.{versionMinor}")
                
    numPoints = binary.read_ulong(file)
    numNormals = binary.read_ulong(file)
    numFaces = binary.read_ulong(file)
    
    file.read(4) # dump unknown flag byte
    
    # Read vertex table
    timePOINTstart = time.time()
    points = [read_vertex(file) for i in range(numPoints)]
    logger.step("Read vertices: %d" % numPoints)
    
    # Read vertex normal table
    normalsDict = {i: read_normal(file) for i in range(numNormals)}
    logger.step("Read vertex normals: %d" % numNormals)
    
    # Read faces
    faces = []
    faceDataDict = {}
    timeFACEstart = time.time()
    for i in range(numFaces):
        newFace = read_face(file)
        faces.append([i[0] for i in newFace[0]])
        faceDataDict[i] = newFace
        
    logger.step("Read faces: %d" % numFaces)
    
    # Construct mesh
    objData = bpy.data.meshes.new("Temp LOD")
    objData.from_pydata(points,[],faces) # from_pydata is both faster than BMesh and does not break when fed invalid geometry
    objData.update(calc_edges=True)
    
    for face in objData.polygons:
        face.use_smooth = True
        
    # Read TAGGs
    bm = bmesh.new()
    bm.from_mesh(objData)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    taggSignature = read_signature(file)
    if taggSignature != "TAGG":
        raise IOError(f"Invalid TAGG section signature: {taggSignature}")
    
    namedSelections, properties = process_taggs(file,bm,additionalData,numPoints,numFaces,logger)
    
    # EOF
    LODresolution = binary.read_float(file)
    logger.step("Resolution signature: %d" % LODresolution)
    
    # Create object
    lodIndex, lodRes = lodutils.get_lod_id(LODresolution)
    lodName = lodutils.format_lod_name(lodIndex,lodRes)
    logger.step("Name: %s" % lodName)
        
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
    
    if len(properties) > 0:
        logger.step("Added named properties: %d" % len(properties))
    
    # Push to Mesh data
    bm.normal_update()
    bm.to_mesh(objData)
    bm.free()
    
    # Create materials
    if 'MATERIALS' in additionalData:
        materialDict = process_materials(objData,faceDataDict,materialDict,prefs)
        logger.step("Assigned materials")
        
    # Apply split normals
    if 'NORMALS' in additionalData and lodIndex in data.LODvisuals: 
        process_normals(objData,faceDataDict,normalsDict)
        logger.step("Applied split normals")
        
    # Add vertex group names to object
    #
    # Blender only allows vertex group names to have up to 63 characters.
    # Since proxy selection names (file paths) are often longer than that,
    # they have to be replaced by formatted placeholders and later looked up
    # from a dictionary when needed.
    selectionPattern = "proxy:(.*)\.(\d{3})"
    proxySelections = {}
    for i,name in enumerate(namedSelections):
        if re.match(selectionPattern,name):
            groupName = "@proxy_%04d" % i
            proxySelections[groupName] = name
            name = groupName
            
        obj.vertex_groups.new(name=name)
    
    if len(proxySelections) > 0:
        logger.step("Added proxy name place holders: %d" % len(proxySelections))
        
    if len(namedSelections) > 0:
        logger.step("Added named selections: %d" % len(namedSelections))
    
    logger.level_down()
    return obj, LODresolution, materialDict, proxySelections

def read_file(operator,context,file):
    addonPreferences = utils.get_addon_preferences(context)
    logger = ProcessLogger()
    logger.step("P3D import from %s" % operator.filepath)
    
    timeFILEstart = time.time()

    additionalData = set()
    
    if operator.allowAdditionalData:
        additionalData = operator.additionalData
    
    version, LODcount = read_file_header(file)
    
    logger.log(f"File version: {version}")
    logger.log(f"Number of LODs: {LODcount}")
    
    
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
    logger.level_up()
    for i in range(LODcount):
        timeLODStart = time.time()
        logger.step("LOD %d" % i)
        
        lodObj, res, materialDict, proxySelections = read_lod(context,file,materialDict,additionalData,logger,addonPreferences)
        
        if operator.validateMeshes:
            lodObj.data.validate(clean_customdata=False)
        
        LODs.append((lodObj,res,proxySelections))
        logger.log("Done in %f sec" % (time.time()-timeLODStart))
        
    logger.level_down()
    
    
    rootCollection = context.scene.collection
    
    build_collections(LODs,operator,rootCollection)
    
    # Set up proxies
    if operator.proxyHandling != 'NOTHING' and 'SELECTIONS' in additionalData:
        process_proxies(LODs,operator,materialDict,addonPreferences)
               
    logger.step("")
    logger.step("P3D Import finished in %f sec" % (time.time()-timeFILEstart))
    