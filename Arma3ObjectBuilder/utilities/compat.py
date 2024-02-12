# Helper functions to handle API compatibility issues between different versions of Blender


import bpy


# Blender 4.0.0 removed the traditional bpy.ops.xyz.xyz(ctx, **kwargs) type operator calling,
# and since the new temp_override method was only introduced late in the 3.x.x versions,
# to maintain compatibility with older releases, the operator call has to be version dependent
# https://developer.blender.org/docs/release_notes/4.0/python_api/#blender-operators-bpyops
def call_operator_ctx(op, ctx = None, **kwargs):
    if not ctx:
        op(**kwargs)
        return
    
    if bpy.app.version > (3, 6, 0):
        with bpy.context.temp_override(**ctx):
            op(**kwargs)
    else:
        op(ctx, **kwargs)


# https://developer.blender.org/docs/release_notes/4.1/python_api/#breaking-changes
def mesh_auto_smooth(mesh):
    if bpy.app.version < (4, 1, 0):
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = 3.141592654