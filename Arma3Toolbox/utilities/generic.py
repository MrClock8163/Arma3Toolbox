import bpy
import math

def show_infoBox(message,title = "",icon = 'INFO'):
    def draw(self,context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw,title = title,icon = icon)
