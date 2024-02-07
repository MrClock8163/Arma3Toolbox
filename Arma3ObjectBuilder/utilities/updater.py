
import bpy


def convert_atbx_lods():
    ...


def convert_atbx_dtm():
    ...


def can_update():
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and hasattr(obj, "armaObjProps") and obj.armaObjProps.isArmaObject:
            return True