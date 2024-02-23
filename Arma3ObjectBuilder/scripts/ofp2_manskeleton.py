#   ---------------------------------------- HEADER ----------------------------------------
#   
#   Author: MrClock
#   Add-on: Arma 3 Object Builder
#   
#   Description:
#       The script adds the OFP2_ManSkeleton to the skeleton list of the Rigging tool panel.
#
#   Usage:
#       1. set settings as necessary
#       2. run script
#   
#   ----------------------------------------------------------------------------------------


#   --------------------------------------- SETTINGS ---------------------------------------

class Settings:
    # Turn all bone names to lowercase
    force_lowercase = True


#   ---------------------------------------- LOGIC -----------------------------------------
    
import bpy

from Arma3ObjectBuilder.utilities import data


def main():
    scene_props = bpy.context.scene.a3ob_rigging
    skeleton = scene_props.skeletons.add()
    skeleton.name = "ofp2_manskeleton" if Settings.force_lowercase else "OFP2_ManSkeleton"
    skeleton.protected = True

    for bone, parent in data.ofp2_manskeleton.items():
        item = skeleton.bones.add()
        item.name = bone.lower() if Settings.force_lowercase else bone
        item.parent = parent.lower() if Settings.force_lowercase else parent


main()