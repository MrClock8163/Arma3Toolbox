# Changelog

## [v2.0.0](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v2.0.0)

**This update brings compatibility with the Blender 4 releases**

### Added:
- LOD object outliner
- option to force lower case bone names during RTM export
- option to force lower case file paths and selection names during P3D export
- option to renumber components during P3D export
- Copy Proxy operator
- Copy Proxies operator
- Transfer Proxies operator
- 4 new proxies in the Common Proxies list
- Vertex Flag Groups
- Face Flag Groups

### Changed:
- updated internal operator calls to be compatible with the new Blender API
- updated Live Mass Editing to be compatible with the new Blender API
- named property operators now correctly operate on object displayed in the properties tab, instead of the active view-layer object
- P3D import and export was completely overhauled
  - file is now first read completely and kept in memory during the import process
  - roughly average **40% decrease in import time**
  - updated import-export logging
  - edges of flat shaded faces are now only exported as sharp, if the entire LOD is flat shaded
- RTM export was completely overhauled

### Fixed:
- RTM export would not delete faulty outputs and raise an exception due to in missing module import
- P3D import would sometimes fail due to mismatching normals-loops counts (on topoologically defective models)
- ASCIIZ strings and characters were mistakenly decoded as UTF-8 (with no practical consequnce)
- P3D output would become potentially faulty if non-manifold edges were marked as sharp

### Removed:
- Dynamic Object Naming (from LOD and proxy objects)
- Vertex Normals Flag LOD object property (use the new Vertex Flag Groups instead)

## [v1.0.0](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v1.0.0)

### Added:
- Move Bottom utility function
- Sort Sections option in P3D export
- custom UI icons (for dark and light UI themes)
- Find Arma 3 Tools function in add-on preferences
- Analyze sub-panel with mass distribution visualization function in Vertex Mass Editing tool panel

### Changed:
- Sort function was renamed to Move Top
- help links are now displayed on property panels as well
- P3D export now only processes visible LOD objects
- multiple functions were updated to not split-merge the meshes and use internal functions instead (eg.: Find Components, Mass From Density etc.)
- Redefine Vertex Group now modifies the existing group instead of removing and recreating it
- Vertex Mass Editing panel items are now always visible
- tool panel properties are now saved in blend files and are persistent across sessions

### Fixed:
- P3D export would fail if a LOD object was in edit mode
- P3D export would fail if a LOD object had a non-mesh child object
- setup conversion would fail with materials using procedural colors
- proxy tools panel would throw exception if no object was active in the scene
- documentation link would not show up in add-on preferences in newer Blender versions
- Component Convex Hull would not actually perform convex hull on all components

### Removed:
- Translucent option in material properties

## [v0.3.4](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.3.4)

### Added:
- support for relative paths (not recommended to be used though)
- option to only import 1st P3D LOD
- option to validate P3D LODs during export

### Changed:
- files during exports are now first written to *.temp files which are cleaned up in case an error occurs
- validation can now be run on all LOD types
- the UVSet0 embedded into the geometry data is no longer discarded during P3D import
- reduced the number of vertex normals written to P3D files by eliminating duplicates

### Fixed:
- fixed an error in the P3D import where random sharp edges would appear on the model under certain conditions
- fixed various back-end issues with edge cases

## [v0.3.3](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.3.3)

### Added:
- new utility functions:
  - Sort faces
  - Recalculate Normals
- Color converter tool
- Weight Painting cleanup tools
- Fixed Vertex Normals option to LOD properties

### Changed:
- file names of UI implementations now represent their context
- exception logging during I/O operations was made cleaner
- documentation links now point to the new GitBook

### Fixed:
- exception would occur in newer Blender versions during vertex mass editing (due to a so-far-unnoticed API difference in the bmesh module)

## [v0.3.2](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.3.2)

### Added:
- Align With Object proxy operator
- Dynamic Object Naming for LOD and proxy objects
- Addon Preference option to show/hide tool help links
- Renaming tools
  - Bulk Rename
  - Root Rename
  - Vertex Groups
- Calculated raster spacing for raster DTMs

### Changed:
- renamed Align Coordinate System operator to Realign Coordinate System

### Fixed:
- proxy transformation issue during import

## [v0.3.1](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.3.1)

### Added:
- Proxies tool panel
- Extract Proxy functionality
- Align Coordinate System functionality

### Changed:
- all tool panels are now collapsed by default
- Vertex Mass Editing panel is now visible in Object Mode too
- LODs are now sorted by their resolution signatures before export

### Fixed:
- the P3D import would fail if there was an object already selected in the scene
- the magazine proxy path in the common proxies list had a typo


## [v0.3.0](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.3.0)

### Added:
- Export - Arma 3 animation (*.rtm)
- RTM Frames tool
- RTM properties
- Setup conversion - DTM
- Setup conversion - Armature

## [v0.2.0](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.2.0)

### Added:
- Import - Esri ASCII grid (*.asc)
- Export - Esri ASCII grid (*.asc)

## [v0.1.0](https://github.com/MrClock8163/Arma3ObjectBuilder/releases/tag/v0.1.0)

Initial release

### Added:
- P3D import (MLOD)
- P3D export (MLOD)
- interfaces to edit all P3D properties
- conversion from ArmaToolbox-style setup
- LOD mesh validation
- hit point cloud generation
