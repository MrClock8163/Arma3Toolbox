"""
blender -b -noaudio --python tests/mcfg.py
"""


import os
import unittest

import bpy


folder_inputs = os.path.join(os.getcwd(), "tests/inputs")
folder_outputs = os.path.join(os.getcwd(), "tests/outputs/mcfg")


class McfgTest(unittest.TestCase):
    """Test cases to test model.cfg handling"""

    def test_import(self):
        """Import sample model.cfg and verify length of contents"""

        bpy.ops.wm.read_homefile(app_template="")

        file_in_mcfg = os.path.join(folder_inputs, "model.cfg")

        bpy.ops.a3ob.import_mcfg(filepath=file_in_mcfg)
        
        scene_props = bpy.context.scene.a3ob_rigging
        self.assertEqual(len(scene_props.skeletons), 1)
        self.assertEqual(len(scene_props.skeletons[0].bones), 18)
    
    def test_export(self):
        """Create skeleton definition and export to model.cfg"""

        bpy.ops.wm.read_homefile(app_template="")

        file_out_mcfg = os.path.join(folder_outputs, "model.cfg")
        scene_props = bpy.context.scene.a3ob_rigging

        skeleton = scene_props.skeletons.add()
        skeleton.name = "Skeleton"

        bone_base = skeleton.bones.add()
        bone_base.name = "bone_0"

        for i in range(10):
            bone = skeleton.bones.add()
            bone.name = ("bone_%d" % (i + 1))
            bone.parent = "bone_0"
        
        bpy.ops.a3ob.export_mcfg(filepath=file_out_mcfg, skeleton_index=0)


def main():
    if not os.path.isdir(folder_outputs):
        os.makedirs(folder_outputs)

    unittest.main(argv=["blender"])


if __name__ == "__main__":
    main()