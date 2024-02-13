"""
blender -b -noaudio --python tests/p3d.py
"""


import os
import unittest

import bpy


folder_inputs = os.path.join(os.getcwd(), "tests/inputs/p3d")
folder_outputs = os.path.join(os.getcwd(), "tests/outputs/p3d")


class P3DTest(unittest.TestCase):
    """Test cases to test P3D related functionalities"""

    def __init__(self, methodName = "runTest"):
        self.inputs = [file for file in os.listdir(folder_inputs) if os.path.splitext(file)[1].lower() == ".p3d"]
        super().__init__(methodName)

    def test_import(self):
        """Import the sample models"""

        for file in self.inputs:
            file_in_p3d = os.path.join(folder_inputs, file)

            bpy.ops.wm.read_homefile(app_template="")
            bpy.ops.a3ob.import_p3d(filepath=file_in_p3d)
    
    def test_import_export(self):
        """Import -> export the sample models, re-import -> re-export the first exported models, and compare size"""

        for file in self.inputs:
            name = os.path.splitext(file)[0]

            file_in_p3d = os.path.join(folder_inputs, file)
            file_out_p3d_1 = os.path.join(folder_outputs, name + "_out.p3d")
            file_out_p3d_2 = os.path.join(folder_outputs, name + "_out_re.p3d")
            
            bpy.ops.wm.read_homefile(app_template="")
            bpy.ops.a3ob.import_p3d(filepath=file_in_p3d)
            bpy.ops.a3ob.export_p3d(filepath=file_out_p3d_1)
            bpy.ops.wm.read_homefile(app_template="")
            bpy.ops.a3ob.import_p3d(filepath=file_out_p3d_1)
            bpy.ops.a3ob.export_p3d(filepath=file_out_p3d_2)

            size_out = os.path.getsize(file_out_p3d_1)
            size_out_re = os.path.getsize(file_out_p3d_2)
            self.assertEqual(size_out, size_out_re, "%s (%d bytes) and %s (%d bytes) are not the same size" % (file_out_p3d_1, size_out, file_out_p3d_2, size_out_re))


def main():
    if not os.path.isdir(folder_inputs):
        os.makedirs(folder_inputs)
    if not os.path.isdir(folder_outputs):
        os.makedirs(folder_outputs)
        
    unittest.main(argv=["blender"])


if __name__ == "__main__":
    main()