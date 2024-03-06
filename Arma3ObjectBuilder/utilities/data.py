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
    31: -1
}


lod_visuals = {0, 1, 2, 3, 18, 30}


lod_shadows = {4, 26, 27, 28}


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
    30: "Underground - Geometry PhysX Old",
    31: "Unknown"
}


lod_groups_type = {
    **dict.fromkeys([0, 1, 2, 3, 18], "Visuals"),
    **dict.fromkeys([4, 26, 27, 28], "Shadows"),
    **dict.fromkeys([6, 7, 8, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 30], "Geometries"),
    **dict.fromkeys([9, 10, 13], "Point clouds"),
    **dict.fromkeys([5, 11, 12, 25, 29, 31], "Misc")
}


lod_groups_context = {
    **dict.fromkeys([0], "3rd person"),
    **dict.fromkeys([1, 2, 3, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28], "1st person"),
    **dict.fromkeys([4, 6], "General"),
    **dict.fromkeys([5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 25, 29, 30, 31], "Misc")
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
    ('30', "Underground (VBS)", "Underground volume for VBS (not supported in Arma 3, Geometry PhysX Old)"),
    ('31', "Unknown", "Unknown model layer")
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


translations_czech_english = {
    # Sprockets
    "koll1": "sprocket_1_1",
    "koll2": "sprocket_1_2",
    "koll3": "sprocket_1_3",
    "koll4": "sprocket_1_4",
    "kolp1": "sprocket_2_1",
    "kolp2": "sprocket_2_2",
    "kolp3": "sprocket_2_3",
    "kolp4": "sprocket_2_4",

    # Wheels
    "kolol1": "wheel_1_1",
    "kolol2": "wheel_1_2",
    "kolol3": "wheel_1_3",
    "kolol4": "wheel_1_4",
    "kolol5": "wheel_1_5",
    "kolol6": "wheel_1_6",
    "kolol7": "wheel_1_7",
    "kolol8": "wheel_1_8",
    "kolol9": "wheel_1_9",
    "kolol10": "wheel_1_10",
    "kolop1": "wheel_2_1",
    "kolop2": "wheel_2_2",
    "kolop3": "wheel_2_3",
    "kolop4": "wheel_2_4",
    "kolop5": "wheel_2_5",
    "kolop6": "wheel_2_6",
    "kolop7": "wheel_2_7",
    "kolop8": "wheel_2_8",
    "kolop9": "wheel_2_9",
    "kolop10": "wheel_2_10",

    # Dampers
    "podkolol1": "wheel_1_1_damper",
    "podkolol2": "wheel_1_2_damper",
    "podkolol3": "wheel_1_3_damper",
    "podkolol4": "wheel_1_4_damper",
    "podkolol5": "wheel_1_5_damper",
    "podkolol6": "wheel_1_6_damper",
    "podkolol7": "wheel_1_7_damper",
    "podkolol8": "wheel_1_8_damper",
    "podkolol9": "wheel_1_9_damper",
    "podkolol10": "wheel_1_10_damper",
    "podkolop1": "wheel_2_1_damper",
    "podkolop2": "wheel_2_2_damper",
    "podkolop3": "wheel_2_3_damper",
    "podkolop4": "wheel_2_4_damper",
    "podkolop5": "wheel_2_5_damper",
    "podkolop6": "wheel_2_6_damper",
    "podkolop7": "wheel_2_7_damper",
    "podkolop8": "wheel_2_8_damper",
    "podkolop9": "wheel_2_9_damper",
    "podkolop10": "wheel_2_10_damper",

    # Damper hides
    "podkolol1_hide": "wheel_1_1_damper_hide",
    "podkolol2_hide": "wheel_1_2_damper_hide",
    "podkolol3_hide": "wheel_1_3_damper_hide",
    "podkolol4_hide": "wheel_1_4_damper_hide",
    "podkolol5_hide": "wheel_1_5_damper_hide",
    "podkolol6_hide": "wheel_1_6_damper_hide",
    "podkolol7_hide": "wheel_1_7_damper_hide",
    "podkolol8_hide": "wheel_1_8_damper_hide",
    "podkolol9_hide": "wheel_1_9_damper_hide",
    "podkolol10_hide": "wheel_1_10_damper_hide",
    "podkolop1_hide": "wheel_2_1_damper_hide",
    "podkolop2_hide": "wheel_2_2_damper_hide",
    "podkolop3_hide": "wheel_2_3_damper_hide",
    "podkolop4_hide": "wheel_2_4_damper_hide",
    "podkolop5_hide": "wheel_2_5_damper_hide",
    "podkolop6_hide": "wheel_2_6_damper_hide",
    "podkolop7_hide": "wheel_2_7_damper_hide",
    "podkolop8_hide": "wheel_2_8_damper_hide",
    "podkolop9_hide": "wheel_2_9_damper_hide",
    "podkolop10_hide": "wheel_2_10_damper_hide",

    # Turrets
    "otocvez": "turret",
    "osaveze": "turret_axis",
    "damagevez": "turret_damage",
    "otochlaven": "gun",
    "otochlavenin": "gun_inside",
    "osahlavne": "gun_axis",
    "damagehlaven": "gun_damage",
    "recoilhlaven": "gun_recoil",
    "recoilhlaven_axis": "gun_recoil_axis",
    "vezvelitele": "commander_tower",
    "otocvelitele": "commander_turret",
    "osavelitele": "commander_turret_axis",
    "zbranvelitele": "commander_weapon",
    "otochlavenvelitele": "commander_gun",
    "osahlavnevelitele": "commander_gun_axis",

    # Hatches
    "poklop_driver": "hatch_driver",
    "osa_poklop_driver": "hatch_driver_axis",
    "poklop_driver_axis": "hatch_driver_axis",
    "poklop_commander": "hatch_commander",
    "osa_poklop_commander": "hatch_commander_axis",
    "poklop_commander_axis": "hatch_commander_axis",
    "poklop_gunner": "hatch_gunner",
    "osa_poklop_gunner": "hatch_gunner_axis",
    "poklop_gunner_axis": "hatch_gunner_axis",
    
    # Weapons
    "usti hlavne": "muzzle_pos",
    "usti hlavne1": "muzzle_pos_1",
    "usti hlavne2": "muzzle_pos_2",
    "usti hlavne3": "muzzle_pos_3",
    "konec hlavne": "muzzle_end",
    "konec hlavne1": "muzzle_end_1",
    "konec hlavne2": "muzzle_end_2",
    "konec hlavne3": "muzzle_end_3",
    "usti granatometu": "muzzle_ugl_pos",
    "konec granatometu": "muzzle_ugl_end",
    "spice rakety": "missile_pos",
    "spice rakety 1": "missile_pos_1",
    "spice rakety 2": "missile_pos_2",
    "konec rakety": "missile_end",
    "konec rakety 1": "missile_end_1",
    "konec rakety 2": "missile_end_2",
    "zasleh": "muzzleflash",
    "zasleh1": "muzzleflash_1",
    "zasleh2": "muzzleflash_2",
    "zasleh3": "muzzleflash_3",

    # Misc
    "kulas": "machinegun",
    "vez": "tower",
    "zbran": "weapon",
    "zbytek": "remainder",
    "telo": "body",
    "palivo": "fuel",
    "motor": "engine",
    "brzdove svetlo": "light_brake",
    "zadni svetlo": "light_rear",
    "doplnovani": "supply",
    "pasoffsetl": "track_l_offset",
    "pasoffsetp": "track_r_offset",
    "pas_l": "track_l",
    "pas_p": "track_r",
    "zamerny": "aimpoint",
    "vrtulea": "propeller_a",
    "vrtuleb": "propeller_b",
    "osavrtulea": "properller_a_axis",
    "osavrtuleb": "properller_b_axis",
    "stopa": "trail",
    "stopa pll": "trail_f_l_l",
    "stopa plp": "trail_f_l_r",
    "stopa ppl": "trail_f_r_l",
    "stopa ppp": "trail_f_r_r",
    "stopa zll": "trail_b_l_l",
    "stopa zlp": "trail_b_l_r",
    "stopa zpl": "trail_b_r_l",
    "stopa zpp": "trail_b_r_r",
    "stopa ll": "trail_l_outer",
    "stopa lr": "trail_l_inner",
    "stopa rl": "trail_r_outer",
    "stopa rr": "trail_r_inner"
}


translations_english_czech = {v: k for k, v in translations_czech_english.items()}


ofp2_manskeleton = {
    "Pelvis": "",
    "Spine": "Pelvis",
    "Spine1": "Spine",
    "Spine2": "Spine1",
    "Spine3": "Spine2",
    "Camera": "Pelvis",
    "weapon": "Spine1",
    "launcher": "Spine1",
    
    # Head skeleton in hierarchy
    "neck": "Spine3",
    "neck1": "neck",
    "head": "neck1",
    
    # New facial features
    "Face_Hub": "head",
    "Face_Jawbone": "Face_Hub",
    "Face_Jowl": "Face_Jawbone",
    "Face_chopRight": "Face_Jawbone",
    "Face_chopLeft": "Face_Jawbone",
    "Face_LipLowerMiddle": "Face_Jawbone",
    "Face_LipLowerLeft": "Face_Jawbone",
    "Face_LipLowerRight": "Face_Jawbone",
    "Face_Chin": "Face_Jawbone",
    "Face_Tongue": "Face_Jawbone",
    "Face_CornerRight": "Face_Hub",
    "Face_CheekSideRight": "Face_CornerRight",
    "Face_CornerLeft": "Face_Hub",
    "Face_CheekSideLeft": "Face_CornerLeft",
    "Face_CheekFrontRight": "Face_Hub",
    "Face_CheekFrontLeft": "Face_Hub",
    "Face_CheekUpperRight": "Face_Hub",
    "Face_CheekUpperLeft": "Face_Hub",
    "Face_LipUpperMiddle": "Face_Hub",
    "Face_LipUpperRight": "Face_Hub",
    "Face_LipUpperLeft": "Face_Hub",
    "Face_NostrilRight": "Face_Hub",
    "Face_NostrilLeft": "Face_Hub",
    "Face_Forehead": "Face_Hub",
    "Face_BrowFrontRight": "Face_Forehead",
    "Face_BrowFrontLeft": "Face_Forehead",
    "Face_BrowMiddle": "Face_Forehead",
    "Face_BrowSideRight": "Face_Forehead",
    "Face_BrowSideLeft": "Face_Forehead",
    "Face_Eyelids": "Face_Hub",
    "Face_EyelidUpperRight": "Face_Hub",
    "Face_EyelidUpperLeft": "Face_Hub",
    "Face_EyelidLowerRight": "Face_Hub",
    "Face_EyelidLowerLeft": "Face_Hub",
    "EyeLeft": "Face_Hub",
    "EyeRight": "Face_Hub",			
    
    # Left upper side
    "LeftShoulder": "Spine3",
    "LeftArm": "LeftShoulder",
    "LeftArmRoll": "LeftArm",
    "LeftForeArm": "LeftArmRoll",
    "LeftForeArmRoll": "LeftForeArm",
    "LeftHand": "LeftForeArmRoll",
    "LeftHandRing": "LeftHand",
    "LeftHandRing1": "LeftHandRing",
    "LeftHandRing2": "LeftHandRing1",
    "LeftHandRing3": "LeftHandRing2",
    "LeftHandPinky1": "LeftHandRing",
    "LeftHandPinky2": "LeftHandPinky1",
    "LeftHandPinky3": "LeftHandPinky2",
    "LeftHandMiddle1": "LeftHand",
    "LeftHandMiddle2": "LeftHandMiddle1",
    "LeftHandMiddle3": "LeftHandMiddle2",
    "LeftHandIndex1": "LeftHand",
    "LeftHandIndex2": "LeftHandIndex1",
    "LeftHandIndex3": "LeftHandIndex2",
    "LeftHandThumb1": "LeftHand",
    "LeftHandThumb2": "LeftHandThumb1",
    "LeftHandThumb3": "LeftHandThumb2",
    
    # Right upper side
    "RightShoulder": "Spine3",
    "RightArm": "RightShoulder",
    "RightArmRoll": "RightArm",
    "RightForeArm": "RightArmRoll",
    "RightForeArmRoll": "RightForeArm",
    "RightHand": "RightForeArmRoll",
    "RightHandRing": "RightHand",
    "RightHandRing1": "RightHandRing",
    "RightHandRing2": "RightHandRing1",
    "RightHandRing3": "RightHandRing2",
    "RightHandPinky1": "RightHandRing",
    "RightHandPinky2": "RightHandPinky1",
    "RightHandPinky3": "RightHandPinky2",
    "RightHandMiddle1": "RightHand",
    "RightHandMiddle2": "RightHandMiddle1",
    "RightHandMiddle3": "RightHandMiddle2",
    "RightHandIndex1": "RightHand",
    "RightHandIndex2": "RightHandIndex1",
    "RightHandIndex3": "RightHandIndex2",
    "RightHandThumb1": "RightHand",
    "RightHandThumb2": "RightHandThumb1",
    "RightHandThumb3": "RightHandThumb2",
    
    # Left lower side
    "LeftUpLeg": "Pelvis",
    "LeftUpLegRoll": "LeftUpLeg",
    "LeftLeg": "LeftUpLegRoll",
    "LeftLegRoll": "LeftLeg",
    "LeftFoot": "LeftLegRoll",
    "LeftToeBase": "LeftFoot",
    
    # Right lower side
    "RightUpLeg": "Pelvis",
    "RightUpLegRoll": "RightUpLeg",
    "RightLeg": "RightUpLegRoll",
    "RightLegRoll": "RightLeg",
    "RightFoot": "RightLegRoll",
    "RightToeBase": "RightFoot"
}


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
        "class": "house",
        "forcenotalpha": "1",
        "lodnoshadow": "1",
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
        "Interior": r"P:\a3\data_f\penetration\vehicle_interior.rvmat",
        "Meat (limbs)": r"P:\a3\data_f\penetration\meat.rvmat",
        "Meat + Bones (body)": r"P:\a3\data_f\penetration\meatbones.rvmat",
        "Plastic": r"P:\a3\data_f\penetration\plastic.rvmat"
    },
    "procedurals": {
        "PIP": "#(argb,512,512,1)r2t(rendertarget0,1.0)"
    }
}