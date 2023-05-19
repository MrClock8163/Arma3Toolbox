lod_resolution_position = { # decimal places in normalized format
    0: -1,
    3: 3,
    4: 4,
    5: 4,
    16: 2,
    26: 2,
    30: -1
}

lod_visuals = (0,1,2,3,18,30)

lod_type_index = {
    (0.0, 0):   0, # Visual
    (1.0, 3):   1, # View Gunner
    (1.1, 3):   2, # View Pilot
    (1.2, 3):   3, # View Cargo
    (1.0, 4):   4, # Shadow
    (2.0, 4):   5, # Edit
    (1.0, 13):  6, # Geometry
    (2.0, 13):  7, # Geometry Buoyancy
    (4.0, 13):  8, # Geometry PhysX
    (1.0, 15):  9, # Memory
    (2.0, 15):  10, # Land Contact
    (3.0, 15):  11, # Roadway
    (4.0, 15):  12, # Paths
    (5.0, 15):  13, # Hit Points
    (6.0, 15):  14, # View Geometry
    (7.0, 15):  15, # Fire Geometry
    (8.0, 15):  16, # View Cargo Geometry
    (9.0, 15):  17, # View Cargo Fire Geometry
    (1.0, 16):  18, # View Commander
    (1.1, 16):  19, # View Commander Geometry
    (1.2, 16):  20, # View Commander Fire Geometry
    (1.3, 16):  21, # View Pilot Geometry
    (1.4, 16):  22, # View Pilot Fire General
    (1.5, 16):  23, # View Gunner Geometry
    (1.6, 16):  24, # View Gunner Fire Geometry
    (1.7, 16):  25, # Sub Parts
    (1.8, 16):  26, # Cargo View Shadow Volume
    (1.9, 16):  27, # Pilot View Shadow Volume
    (2.0, 16):  28, # Gunner View Shadow Volume
    (2.1, 16):  29, # Wreckage
    (-1.0, 0):  30 # Unknown
}

lod_type_names = {
    0:  ("Resolution", "Visual resolution"),
    1:  ("View - Gunner", "Gunner first person view"),
    2:  ("View - Pilot", "First person view"),
    3:  ("View - Cargo", "Passenger first person view"),
    4:  ("Shadow Volume", "Shadow casting geometry"),
    5:  ("Edit", "Temporary layer"),
    6:  ("Geometry", "Object collision geometry and occluders"),
    7:  ("Geometry Buoyancy", "Buoyant object geometry"),
    8:  ("Geometry PhysX", "PhysX object collision geometry"),
    9:  ("Memory", "Hard points and animation axes"),
    10: ("Land Contact", "Points of contact with ground"),
    11: ("Roadway", "Walkable surfaces"),
    12: ("Paths", "AI path finding mesh"),
    13: ("Hit-points", "Hit point cloud"),
    14: ("View Geometry", "View occlusion for AI"),
    15: ("Fire Geometry", "Hitbox geometry"),
    16: ("View - Cargo Geometry", "Passenger view collision geometry and occluders"),
    17: ("View - Cargo Fire Geometry", "Passenger view hitbox geometry"),
    18: ("View - Commander", "Commander first person view"),
    19: ("View - Commander Geometry", "Commander view collision geometry and occluders"),
    20: ("View - Commander Fire Geometry", "Commander hitbox geometry"),
    21: ("View - Pilot Geometry", "First person collision geometry and occluders"),
    22: ("View - Pilot Fire Geometry", "First person hitbox geometry"),
    23: ("View - Gunner Geometry", "Gunner collision geometry and occluders"),
    24: ("View - Gunner Fire Geometry", "Gunner view hitbox geometry"),
    25: ("Sub Parts", "Obsolete"),
    26: ("Shadow Volume - Cargo View", "Passenger view shadow casting geometry"),
    27: ("Shadow Volume - Pilot View", "First person view shadow casting geometry"),
    28: ("Shadow Volume - Gunner View", "Gunner view shadow casting geometry"),
    29: ("Wreckage", "Vehicle wreckage"),
    30: ("Unknown", "Unknown model layer")
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

common_namedprops = {
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
}

common_proxies = {
    "Weapon optic": r"P:\a3\data_f\proxies\weapon_slots\top.p3d",
    "Weapon pointer": r"P:\a3\data_f\proxies\weapon_slots\side.p3d",
    "Weapon suppressor": r"P:\a3\data_f\proxies\weapon_slots\muzzle.p3d",
    "Weapon magazine": r"P:\a3\data_f\proxies\weapon_slots\magazine.p3d",
    "Weapon bipod": r"P:\a3\data_f_mark\proxies\weapon_slots\underbarrel.p3d"
}