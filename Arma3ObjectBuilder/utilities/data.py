# Various hard coded data used in I/O and throughout the UI.


flags_vertex_surface = {
    'NORMAL': 0x00000000,
    'SURFACE_ON': 0x00000001,
    'SURFACE_ABOVE': 0x00000002,
    'SURFACE_UNDER': 0x00000004,
    'KEEP_HEIGHT': 0x00000008
}


flags_vertex_fog = {
    'NORMAL': 0x00000000,
    'SKY': 0x00002000,
    'NONE': 0x00001000
}


flags_vertex_decal = {
    'NORMAL': 0x00000000,
    'DECAL': 0x00000100
}


flags_vertex_lighting = {
    'NORMAL': 0x00000000,
    'SHINING': 0x00000010,
    'SHADOW': 0x00000020,
    'LIGHTED_HALF': 0x00000080,
    'LIGHTED_FULL': 0x00000040
}


flags_vertex_normals = {
    'AREA': 0x00000000,
    'ANGLE': 0x04000000,
    'FIXED': 0x02000000
}


flag_vertex_hidden = 0x01000000


flags_face_lighting = {
    'NORMAL': 0x00000000,
    'BOTH': 0x00000020,
    'POSITION': 0x00000080,
    'FLAT': 0x00100000,
    'REVERSED': 0x00200000
}


flags_face_zbias = {
    'NONE': 0x00000000,
    'LOW': 0x00000100,
    'MIDDLE': 0x00000200,
    'HIGH': 0x00000300
}


flag_face_noshadow = 0x00000010
flag_face_merging = 0x01000000
flag_face_user_mask = 0xfe000000


lod_resolution_position = { # decimal places in normalized format
    0: -1,
    3: 3,
    4: 4,
    5: 4,
    16: 2,
    26: 2,
    30: -1
}


lod_resolution = (0, 3, 4, 5, 16, 26, 30)


lod_visuals = (0, 1, 2, 3, 18, 30)


lod_shadows = (4, 26, 27, 28)


lod_type_names = {
    0: "Resolution",
    1: "View - Gunner",
    2: "View - Pilot",
    3: "View - Cargo",
    4: "Shadow Volume",
    5: "Edit",
    6: "Geometry",
    7: "Geometry Buoyancy",
    8: "Geometry PhysX",
    9: "Memory",
    10: "Land Contact",
    11: "Roadway",
    12: "Paths",
    13: "Hit-points",
    14: "View Geometry",
    15: "Fire Geometry",
    16: "View - Cargo Geometry",
    17: "View - Cargo Fire Geometry",
    18: "View - Commander",
    19: "View - Commander Geometry",
    20: "View - Commander Fire Geometry",
    21: "View - Pilot Geometry",
    22: "View - Pilot Fire Geometry",
    23: "View - Gunner Geometry",
    24: "View - Gunner Fire Geometry",
    25: "Sub Parts",
    26: "Shadow Volume - Cargo View",
    27: "Shadow Volume - Pilot View",
    28: "Shadow Volume - Gunner View",
    29: "Wreckage",
    30: "Unknown"
}


lod_groups_type = {
    **dict.fromkeys([0, 1, 2, 3, 18], "Visuals"),
    **dict.fromkeys([4, 26, 27, 28], "Shadows"),
    **dict.fromkeys([6, 7, 8, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24], "Geometries"),
    **dict.fromkeys([9, 10, 13], "Point clouds"),
    **dict.fromkeys([5, 11, 12, 25, 29, 30], "Misc")
}


lod_groups_context = {
    **dict.fromkeys([0], "3rd person"),
    **dict.fromkeys([1, 2, 3, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28], "1st person"),
    **dict.fromkeys([4, 6], "General"),
    **dict.fromkeys([5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 25, 29, 30], "Misc")
}


lod_groups = {
    'TYPE': lod_groups_type,
    'CONTEXT': lod_groups_context,
    'NONE': {}
}


# Enum property lists
enum_texture_types = (
    ('CO', "CO", "Color Value"),
    ('CA', "CA", "Texture with Alpha"),
    ('LCO', "LCO", "Terrain Texture Layer Color"),
    ('SKY', "SKY", "Sky texture"),
    ('NO', "NO", "Normal Map"),
    ('NS', "NS", "Normal map specular with Alpha"),
    ('NOF', "NOF", "Normal map faded"),
    ('NON', "NON", "Normal map noise"),
    ('NOHQ', "NOHQ", "Normal map High Quality"),
    ('NOPX', "NOPX", "Normal Map with paralax"),
    ('NOVHQ', "NOVHQ", "two-part DXT5 compression"),
    ('DT', "DT", "Detail Texture"),
    ('CDT', "CDT", "Colored detail texture"),
    ('MCO', "MCO", "Multiply color"),
    ('DTSMDI', "DTSMDI", "Detail SMDI map"),
    ('MC', "MC", "Macro Texture"),
    ('AS', "AS", "Ambient Shadow texture"),
    ('ADS', "ADS", "Ambient Shadow in Blue"),
    ('PR', "PR", "Ambient shadow from directions"),
    ('SM', "SM", "Specular Map"),
    ('SMDI', "SMDI", "Specular Map, optimized"),
    ('MASK', "MASK", "Mask for multimaterial"),
    ('TI', "TI", "Thermal imaging map")
)


enum_lod_types = (
    ('0', "Resolution", "Visual resolutiion"),
    ('1', "View - Gunner", "Gunner first person view"),
    ('2', "View - Pilot", "First person view"),
    ('3', "View - Cargo", "Passenger first person view"),
    ('4', "Shadow Volume", "Shadow casting geometry"),
    ('5', "Edit", "Temporary layer"),
    ('6', "Geometry", "Object collision geometry and occluders"),
    ('7', "Geometry Buoyancy", "Buoyant object geometry"),
    ('8', "Geometry PhysX", "PhysX object collision geometry"),
    ('9', "Memory", "Hard points and animation axes"),
    ('10', "Land Contact", "Points of contact with ground"),
    ('11', "Roadway", "Walkable surfaces"),
    ('12', "Paths", "AI path finding mesh"),
    ('13', "Hit-points", "Hit point cloud"),
    ('14', "View Geometry", "View occlusion for AI"),
    ('15', "Fire Geometry", "Hitbox geometry"),
    ('16', "View - Cargo Geometry", "Passenger view collision geometry and occluders"),
    ('17', "View - Cargo Fire Geometry", "Passenger view hitbox geometry"),
    ('18', "View - Commander", "Commander first person view"),
    ('19', "View - Commander Geometry", "Commander view collision geometry and occluders"),
    ('20', "View - Commander Fire Geometry", "Commander hitbox geometry"),
    ('21', "View - Pilot Geometry", "First person collision geometry and occluders"),
    ('22', "View - Pilot Fire Geometry", "First person hitbox geometry"),
    ('23', "View - Gunner Geometry", "Gunner collision geometry and occluders"),
    ('24', "View - Gunner Fire Geometry", "Gunner view hitbox geometry"),
    ('25', "Sub Parts", "Obsolete"),
    ('26', "Shadow Volume - Cargo View", "Passenger view shadow casting geometry"),
    ('27', "Shadow Volume - Pilot View", "First person view shadow casting geometry"),
    ('28', "Shadow Volume - Gunner View", "Gunner view shadow casting geometry"),
    ('29', "Wreckage", "Vehicle wreckage"),
    ('30', "Unknown", "Unknown model layer")
)


# Currently unused as the search function for string properties is a
# relatively new addition and not supported by older Blender versions
# known_namedprops = {
#     "animated": [],
#     "aicovers": ["0", "1"],
#     "armor": [],
#     "autocenter": ["0", "1"],
#     "buoyancy": ["0", "1"],
#     "cratercolor": [],
#     "canbeoccluded": ["0", "1"],
#     "canocclude": ["0", "1"],
#     "class": [
#         "breakablehouseanimated",
#         "bridge",
#         "building",
#         "bushhard",
#         "bushsoft",
#         "church",
#         "clutter",
#         "forest",
#         "house",
#         "housesimulated",
#         "land_decal",
#         "man",
#         "none",
#         "pond",
#         "road",
#         "streetlamp",
#         "thing",
#         "thingx",
#         "tower",
#         "treehard",
#         "treesoft",
#         "vehicle",
#         "wall"
#     ],
#     "damage": [
#         "building",
#         "engine",
#         "no",
#         "tent",
#         "tree",
#         "wall",
#         "wreck"
#     ],
#     "destroysound": [
#         "treebroadleaf",
#         "treepalm"
#     ],
#     "drawimportance": [],
#     "explosionshielding": [],
#     "forcenotalpha": ["0", "1"],
#     "frequent": ["0", "1"],
#     "keyframe": ["0", "1"],
#     "loddensitycoef": [],
#     "lodnoshadow": ["0", "1"],
#     "map": [
#         "main road",
#         "road",
#         "track",
#         "trail",
#         "building",
#         "fence",
#         "wall",
#         "bush",
#         "small tree",
#         "tree",
#         "rock",
#         "bunker",
#         "fortress",
#         "fuelstation",
#         "hospital",
#         "lighthouse",
#         "quay",
#         "view-tower",
#         "ruin",
#         "busstop",
#         "church",
#         "chapel",
#         "cross",
#         "fountain",
#         "power lines",
#         "powersolar",
#         "powerwave",
#         "powerwind",
#         "railway",
#         "shipwreck",
#         "stack",
#         "tourism",
#         "transmitter",
#         "watertower",
#         "hide"
#     ],
#     "mass": [],
#     "maxsegments": [],
#     "minsegments": [],
#     "notl": [],
#     "placement": [
#         "slope",
#         "slopez",
#         "slopex",
#         "slopelandcontact",
#         "vertical"
#     ],
#     "prefershadowvolume": ["0", "1"],
#     "reversed": [],
#     "sbsource": [
#         "explicit",
#         "none",
#         "shadow",
#         "shadowvolume",
#         "visual",
#         "visualex"
#     ],
#     "shadow": ["hybrid"],
#     "shadowlod": [],
#     "shadowvolumelod": [],
#     "shadowbufferlod": [],
#     "shadowbufferlodvis": [],
#     "shadowoffset": [],
#     "viewclass": [],
#     "viewdensitycoef": [],
#     "xcount": [],
#     "xsize": [],
#     "xstep": [],
#     "ycount": [],
#     "ysize": []
# }


common_data = {
    "proxies": {
        "Weapon: optic": r"P:\a3\data_f\proxies\weapon_slots\top.p3d",
        "Weapon: pointer": r"P:\a3\data_f\proxies\weapon_slots\side.p3d",
        "Weapon: suppressor": r"P:\a3\data_f\proxies\weapon_slots\muzzle.p3d",
        "Weapon: magazine": r"P:\a3\data_f\proxies\weapon_slots\magazineslot.p3d",
        "Weapon: bipod": r"P:\a3\data_f_mark\proxies\weapon_slots\underbarrel.p3d",
        "Driver: offroad": r"P:\a3\data_f\proxies\passenger_low01\cargo01.p3d",
        "Gunner: hunter": r"P:\a3\data_f\proxies\gunner_hunter\gunner.p3d",
        "Commander: hunter": r"P:\a3\data_f\proxies\gunner_hunter\commander.p3d",
        "Light volume: car": r"P:\a3\data_f\volumelightcar.p3d"
    },
    "namedprops": {
        "autocenter": "0",
        "buoyancy": "1",
        "class": "building",
        "class": "house",
        "forcenotalpha": "1",
        "lodnoshadow": "1",
        "map": "building",
        "map": "hide",
        "map": "house",
        "prefershadowvolume": "1"
    },
    "materials": {
        "Glass": r"P:\a3\data_f\glass_veh.rvmat",
        "Collimator": r"P:\a3\weapons_f\acc\data\collimdot_cshader.rvmat",
        "VR Armor Emissive": r"P:\a3\characters_f_bootcamp\common\data\vrarmoremmisive.rvmat"
    },
    "materials_penetration": {
        "Armor": r"P:\a3\data_f\penetration\armour.rvmat",
        "Armor Plate": r"P:\a3\data_f\penetration\armour_plate.rvmat",
        "Engine": r"P:\a3\data_f\penetration\engine.rvmat",
        "Fuel tank": r"P:\a3\data_f\penetration\fueltank.rvmat",
        "Glass": r"P:\a3\data_f\penetration\glass.rvmat",
        "Interior": r"P:\a3\data_f\penetration\vehicle_interior.rvmat"
    },
    "procedurals": {
        "PIP": "#(argb,512,512,1)r2t(rendertarget0,1.0)"
    }
}