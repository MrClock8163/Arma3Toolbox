# Arma 3 Object Builder

## About the project

**Arma 3 Object Builder** borrows it's name from the infamous **Object Builder** application that's used for importing models to the P3D model format of **Arma 3**.
While **Object Builder** bares some modelling functionality, it's by no means adequate by today's standards.
Because of this, the need arose to create an alternative, and so Alwarren developed the [**ArmAToolbox**](https://github.com/AlwarrenSidh/ArmAToolbox),
which makes it possible to import and export animation and model files for **Arma 3**.

This project's goal is to build a new, more modern add-on based on the ideas of the original **ArmAToolbox**, which has been in use by modders for many years.
Since it's release, the code base of the **ArmAToolbox** became quite cluttered with unused code and broken features (eg.: due to **Blender** API changes).
This project aims to correct this, and bring elements of the workflow more in-line with the design of **Blender**, while also creating new tools to further aid mod development.

## Origins
The project is originally a fork of Alwarren's repository, but in reality, instead of consisting of smaller changes to be merged into the main repository,
it turned into a full rewrite of the add-on.

Excerpt from the ArmAToolbox readme:
```
Arma Toolbox for Blender
This is a collection of Python scripts for the Blender 3D package
that allows the user to create, import and export unbinarized
Arma Engine .p3d files.
```

## Requirements
- [**Blender** v2.90.0](https://www.blender.org/download/releases/2-90/) or higher
- [**Arma 3 Tools**](https://store.steampowered.com/app/233800/Arma_3_Tools/) (optional for some features to work)

The add-on is developed on **Blender** v2.90.0 for convenience reasons, which also has the side effect that
it supports older versions, not just the latest releases. The add-on is tested on newer releases regardless.
If a new release of **Blender** in the future renders it impossible to keep the add-on compatible with both old, 
and new releases, support will be dropped for legacy versions in favor of the new API.

# License
As inherited from the **ArmAToolbox**, the **Arma 3 Object Builder** add-on is released under the GNU General Public License version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR  PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

Files created using this software are not covered by this license.
