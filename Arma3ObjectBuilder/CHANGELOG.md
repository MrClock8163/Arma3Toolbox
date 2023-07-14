# Changelog

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
