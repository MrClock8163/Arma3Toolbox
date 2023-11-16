import bpy


def call_operator_ctx(op, ctx = None, **kwargs):
    if not ctx:
        op(**kwargs)
        return
    
    if bpy.app.version > (3, 6, 0):
        with bpy.context.temp_override(**ctx):
            op(**kwargs)
    else:
        op(ctx, **kwargs)