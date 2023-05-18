import bpy
import bmesh
import os
import struct
import mathutils
import time
from . import binary_handler as binary
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import proxy as proxyutils
from ..utilities import structure as structutils
from ..utilities import data
from ..utilities.logger import ProcessLogger
    
# may be worth looking into bpy.ops.object.convert(target='MESH') instead to reduce operator calls
def apply_modifiers(obj,context):
    ctx = context.copy()
    ctx["object"] = obj
    
    for m in obj.modifiers:
        try:
            ctx["modifier"] = m
            bpy.ops.object.modifier_apply(ctx,modifier=m.name)
        except:
            newObj.modifiers.remove(m)
            
def merge_objects(mainObj,subObjs,context):
    ctx = context.copy()
    ctx["active_object"] = mainObj
    ctx["selected_objects"] = (subObjs + [mainObj])
    ctx["selected_editable_objects"] = (subObjs + [mainObj])
    
    bpy.ops.object.join(ctx)
        
def duplicate_object(obj):
    newObj = obj.copy()
    newObj.data = obj.data.copy()
    
    return newObj
    
def get_texture_string(materialProps,prefs):
    textureType = materialProps.textureType
    
    if textureType == 'TEX':
        return format_path(materialProps.texturePath,prefs.projectRoot,prefs.exportRelative)
    elif textureType == 'COLOR':
        color = materialProps.colorValue
        return f"#(argb,8,8,3)color({round(color[0],3)},{round(color[1],3)},{round(color[2],3)},{round(color[3],3)},{materialProps.colorType})"
    elif textureType == 'CUSTOM':
        return materialProps.colorString
    else:
        return ""
        
def get_material_string(materialProps,prefs):
    return format_path(materialProps.materialPath,prefs.projectRoot,prefs.exportRelative)
    
def get_proxy_string(OBprops,prefs):
    path = format_path(OBprops.proxyPath,prefs.projectRoot,prefs.exportRelative,True)
    if path[0] != "\\":
        path = "\\" + path
        
    string = f"proxy:{path}.{'%03d' % OBprops.proxyIndex}"
        
    return string

def format_path(path,root = "",makeRelative = True,stripExtension = False):
    path = utils.replace_slashes(path.strip())
    
    if makeRelative:
        root = utils.replace_slashes(root.strip())
        path = utils.make_relative(path,root)
        
    if stripExtension:
        path = utils.strip_extension(path)
        
    return path

def get_lod_data(operator,context):
    addonPreferences = utils.get_addon_preferences(context)
    scene = context.scene
    exportObjects = scene.objects
    
    if operator.use_selection:
        exportObjects = context.selected_objects
    
    LODs = []
    materials = []
    proxies = []
    
    for obj in exportObjects:
        if obj.type != 'MESH' or not obj.a3ob_properties_object.isArma3LOD or obj.parent != None or obj.a3ob_properties_object.LOD == '30':
            continue
            
        mainObj = duplicate_object(obj)
        
        if operator.apply_modifiers:
            apply_modifiers(mainObj,context)
        
        children = obj.children
        
        subObjects = []
        objProxies = {}
        for i,child in enumerate(children):
            if obj.type != 'MESH':
                continue
                
            subObj = duplicate_object(child)
            OBprops = subObj.a3ob_properties_object_proxy
            if OBprops.isArma3Proxy:
                placeholder = "@proxy_%04d" % i
                utils.create_selection(subObj,placeholder)
                objProxies[placeholder] = get_proxy_string(OBprops,addonPreferences)
            
            if operator.apply_modifiers:
                apply_modifiers(subObj,context)
            
            subObjects.append(subObj)
            
        if len(subObjects) > 0:
            merge_objects(mainObj,subObjects,context)
        
        for obj in subObjects:
            bpy.data.meshes.remove(obj.data,do_unlink=True)
        
        if operator.apply_transforms:
            bpy.ops.object.transform_apply({"active_object": mainObj, "selected_editable_objects": [mainObj]},location = True, scale = True, rotation = True)
        
        if operator.validate_meshes:
            mainObj.data.validate(clean_customdata=False)
            
        if not operator.preserve_normals:
            ctx = context.copy()
            ctx["active_object"] = mainObj
            ctx["object"] = mainObj
            bpy.ops.mesh.customdata_custom_splitnormals_clear(ctx)
        
        LODs.append(mainObj)
        proxies.append(objProxies)
        
        objMaterials = {0: ("","")}
        translucency = {0: False}
        
        for i,slot in enumerate(mainObj.material_slots):
            mat = slot.material
            if mat:
                objMaterials[i] = (get_texture_string(mat.a3ob_properties_material,addonPreferences),get_material_string(mat.a3ob_properties_material,addonPreferences))
                translucency[i] = mat.a3ob_properties_material.translucent
            else:
                objMaterials[i] = ("","")
                translucency[i] = False
                
        materials.append(objMaterials)
                
        bm = bmesh.new()
        bm.from_mesh(mainObj.data)
        bm.faces.ensure_lookup_table()
        
        indexOffset = len(bm.faces)-1
        translucentCount = 0
        for face in bm.faces:
            if translucency[face.material_index]:
                face.index = indexOffset + translucentCount
                translucentCount += 1
                
        bm.faces.sort()
        bm.to_mesh(mainObj.data)
        bm.free()
                
    return LODs,materials,proxies
    
def can_export(operator,context):
    scene = context.scene
    exportObjects = scene.objects
    
    if operator.use_selection:
        exportObjects = context.selected_objects
        
    for obj in exportObjects:
        if obj.type == 'MESH' and obj.a3ob_properties_object.isArma3LOD and obj.parent == None and obj.a3ob_properties_object.LOD != '30':
            return True
            
    return False
    
def get_resolution(obj):
    OBprops = obj.a3ob_properties_object
    
    return lodutils.getLODvalue(int(OBprops.LOD),OBprops.resolution)

def encode_selection_weight(weight):
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
    binary.write_ulong(file,0)
    
def write_normal(file,normal):
    file.write(struct.pack('<fff',-normal[0],-normal[2],-normal[1]))

def write_face_pseudo_vertextable(file,loop,uv_layer):
    binary.write_ulong(file,loop.vert.index)
    binary.write_ulong(file,loop.index)
    
    if not uv_layer:
        file.write(struct.pack('<ff',0,0))
    
    file.write(struct.pack('<ff',loop[uv_layer].uv[0],1-loop[uv_layer].uv[1]))

def write_face(file,bm,face,materials,uv_layer):
    numSides = len(face.loops)
    binary.write_ulong(file,numSides)
    
    for i in range(numSides):
        write_face_pseudo_vertextable(file,face.loops[i],uv_layer)
        
    if numSides < 4:
        file.write(struct.pack('<4I',0,0,0,0)) # empty filler for triangles
    
    matData = materials[face.material_index]
    
    binary.write_ulong(file,0) # face flags
    binary.write_asciiz(file,matData[0]) # texture
    binary.write_asciiz(file,matData[1]) # material
    
def write_tagg_sharps_edges(file,bm):
    binary.write_byte(file,1)
    binary.write_asciiz(file,"#SharpEdges#")
    dataSizePos = file.tell()
    binary.write_ulong(file,0) # temporary placeholder value
    
    flatFaceEdges = set()
    for face in bm.faces:
        if not face.smooth:
            flatFaceEdges.update({edge for edge in face.edges})
    
    for edge in bm.edges:
        if not edge.smooth or edge in flatFaceEdges:
            file.write(struct.pack('<II',edge.verts[0].index,edge.verts[1].index))

    dataEndPos = file.tell()
    file.seek(dataSizePos,0)
    binary.write_ulong(file,dataEndPos-dataSizePos-4) # fill in length data
    file.seek(dataEndPos,0)

def write_tagg_uv_sets_item(file,bm,layer,index):
    binary.write_byte(file,1)
    binary.write_asciiz(file,"#UVSet#")
    dataSizePos = file.tell()
    binary.write_ulong(file,0) # temporary placeholder value
    binary.write_ulong(file,index)
    
    for face in bm.faces:
        for loop in face.loops:
            file.write(struct.pack('<ff',loop[layer].uv[0],1-loop[layer].uv[1]))
        
    dataEndPos = file.tell()
    file.seek(dataSizePos,0)
    binary.write_ulong(file,dataEndPos-dataSizePos-4) # fill in length data
    file.seek(dataEndPos,0)

def write_tagg_uv_sets(file,bm,logger):
    index = 0
    for layer in bm.loops.layers.uv.values():
        write_tagg_uv_sets_item(file,bm,layer,index)
        index += 1
        
    logger.step("Wrote UV sets: %d" % index)

def write_tagg_mass(file,bm,numVerts):
    layer = bm.verts.layers.float.get('a3ob_mass')
    if not layer:
        return
        
    binary.write_byte(file,1)
    binary.write_asciiz(file,"#Mass#")
        
    binary.write_ulong(file,numVerts*4)
    
    for vertex in bm.verts:
        binary.write_float(file,vertex[layer])
    
def write_tagg_selections_item(file,name,count_vert,count_face,vertices,faces,proxies):
    real_name = name
    if name.strip().startswith("@proxy"):
        try:
            real_name = proxies[name]
        except:
            pass
            
    binary.write_byte(file,1)
    binary.write_asciiz(file,real_name)
    dataSizePos = file.tell()
    binary.write_ulong(file,0) # temporary placeholder value

    bytes_vert = bytearray(count_vert) # array of 0x0 bytes (effective because this way not every vertex has to be iterated)

    for vertex in vertices:
        bytes_vert[vertex[0]] = encode_selection_weight(vertex[1])
        
    file.write(bytes_vert)

    bytes_face = bytearray(count_face)
    for face in faces:
        bytes_face[face] = 1
        
    file.write(bytes_face)

    dataEndPos = file.tell()
    file.seek(dataSizePos,0)
    binary.write_ulong(file,dataEndPos-dataSizePos-4) # fill in length data
    file.seek(dataEndPos,0)
    
def write_tagg_selections(file,obj,proxies,logger):
    mesh = obj.data
    
    # Build selection database for faster lookup
    selections_vert = {}
    selections_face = {}
    
    for group in obj.vertex_groups:
        selections_vert[group.name] = set()
        selections_face[group.name] = set()
    
    for vertex in mesh.vertices:
        for group in vertex.groups:
            name = obj.vertex_groups[group.group].name
            weight = group.weight
            selections_vert[name].add((vertex.index,weight))
            
    for face in mesh.polygons:
        groups = set([group.group for vertex in face.vertices for group in mesh.vertices[vertex].groups])
        
        for group_id in groups:
            weight = sum([group.weight for vertex in face.vertices for group in mesh.vertices[vertex].groups if group.group == group_id])
            if weight > 0:
                name = obj.vertex_groups[group_id].name
                selections_face[name].add(face.index)
    
    count_vert = len(mesh.vertices)
    count_face = len(mesh.polygons)
    
    for i,group in enumerate(obj.vertex_groups):
        name = group.name
        write_tagg_selections_item(file,name,count_vert,count_face,selections_vert[name],selections_face[name],proxies)
        
    logger.step("Wrote named selections: %d" % (i + 1))
    
def write_tagg_named_properties_item(file,key,value):
    binary.write_byte(file,1)
    binary.write_asciiz(file,"#Property#")
    binary.write_ulong(file,128)
    file.write(struct.pack('<64s',key.encode('ASCII')))
    file.write(struct.pack('<64s',value.encode('ASCII')))
    
def write_tagg_named_properties(file,obj):
    OBprops = obj.a3ob_properties_object
    
    writtenProps = set()
    for prop in OBprops.properties:
        if prop.name not in writtenProps:
            writtenProps.add(prop.name)
            write_tagg_named_properties_item(file,prop.name,prop.value)

def write_file_header(file,LODcount):
    binary.write_chars(file,'MLOD')
    binary.write_ulong(file,257)
    binary.write_ulong(file,LODcount)
    
def write_lod(file,obj,materials,proxies,logger):
    logger.level_up()
    for face in obj.data.polygons:
        if len(face.vertices) > 4:
            OBprops = obj.a3ob_properties_object
            logger.step("N-gons detected -> skipping LOD")
            return False
    
    binary.write_chars(file,'P3DM')
    binary.write_ulong(file,0x1c)
    binary.write_ulong(file,0x100)
    
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
        
    mesh = obj.data
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
    
    binary.write_ulong(file,numVerts)
    binary.write_ulong(file,numLoops) # number of normals
    binary.write_ulong(file,numFaces)
    
    binary.write_ulong(file,0) # unknown flags/padding
    
    for vert in bm.verts:
        write_vertex(file,vert.co)
        
    logger.step("Wrote veritces: %d" % numVerts)
        
    for loop in mesh.loops:
        write_normal(file,loop.normal)
        
    logger.step("Wrote vertex normals: %d" % numLoops)
        
    first_uv_layer = None
    if len(bm.loops.layers.uv.values()) > 0: # 1st UV set needs to be written into the face data section too
        first_uv_layer = bm.loops.layers.uv.values()[0]
        
    for face in bm.faces:
        write_face(file,bm,face,materials,first_uv_layer)
        
    logger.step("Wrote faces: %d" % numFaces)
        
    binary.write_chars(file,'TAGG') # TAGG section start
    
    write_tagg_sharps_edges(file,bm)
    write_tagg_uv_sets(file,bm,logger)
    
    if obj.a3ob_properties_object.LOD == '6':
        write_tagg_mass(file,bm,numVerts) # need to make sure to only export for Geo LODs
        logger.step("Wrote vertex mass")
        
    write_tagg_named_properties(file,obj)
    if len(obj.vertex_groups) > 0:
        write_tagg_selections(file,obj,proxies,logger)
    
    binary.write_byte(file,1)
    binary.write_asciiz(file,"#EndOfFile#") # EOF signature
    binary.write_ulong(file,0)
    
    binary.write_float(file,get_resolution(obj)) # LOD resolution index
    logger.step("Resolution signature: %d" % float(get_resolution(obj)))
    logger.step("Name: %s" % f"{data.LODdata[int(obj.a3ob_properties_object.LOD)][0]} {obj.a3ob_properties_object.resolution}")
    bm.free()
    
    logger.level_down()
    return True

def write_file(operator,context,file):
    logger = ProcessLogger()
    logger.step("P3D export to %s" % operator.filepath)
    
    time_file_start = time.time()
    
    LODobjects, materials, proxies = get_lod_data(operator,context)
    
    LODcount = len(LODobjects)
    logger.log("Detected %d LOD objects" % LODcount)
    
    write_file_header(file,LODcount)
    
    logger.level_up()
    exported_count = 0
    for i,obj in enumerate(LODobjects):
        time_lod_start = time.time()
        logger.step("LOD %d" % i)
        
        success = write_lod(file,obj,materials[i],proxies[i],logger)
        if success:
            exported_count += 1
            
        bpy.data.meshes.remove(obj.data,do_unlink=True)
        
        logger.log("Done in %f sec" % (time.time()-time_lod_start))
    logger.level_down()
    
    logger.step("")
    logger.step("P3D export finished in %f sec" % (time.time() - time_file_start))
    
    return LODcount,exported_count