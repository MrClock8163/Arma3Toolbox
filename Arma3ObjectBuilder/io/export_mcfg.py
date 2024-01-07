

from . import data_rap as rap
from ..utilities import rigging as riggingutils


def write_file(operator, skeleton, file):
    bones_parents = riggingutils.bone_order_from_skeleton(skeleton)
    if bones_parents is None:
        return False
    
    if operator.force_lowercase:
        bones_parents = {k.lower(): v.lower for k, v in bones_parents.items()}
    
    printer = rap.CfgFormatter(file)

    printer.class_open("CfgSkeletons")
    printer.class_open(skeleton.name)

    printer.property_int("isDiscrete", 0)
    printer.property_string("skeletonInherit", "")

    printer.array_open("skeletonBones")
    printer.array_items(["\"%s\", \"%s\"" % (k, v) for k, v in bones_parents.items()])
    printer.array_close()
    printer.comment("Path to the pivot points model has to be set manually")
    printer.property_string("pivotsModel", "")
    
    printer.class_close()
    printer.class_close()

    return True