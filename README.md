# Arma 3 Object Builder

## About the project

**Arma 3 Object Builder** borrows its name from the infamous **Object Builder** application that's used for importing models to the P3D model format of **Arma 3**.
While **Object Builder** bares some modelling functionality, it's by no means adequate by today's standards.
Because of this, the need arose for an alternative, that resulted in the creation of the [**ArmAToolbox**](https://github.com/AlwarrenSidh/ArmAToolbox) add-on for **Blender** by Alwarren,
which makes it possible to import and export animations and models to the **Arma 3** file formats directly.

The **ArmaToolbox** has been in use by modders for many years, but since its release the code base of the add-on became cluttered with unused or broken parts (usually due to changes in the **Blender** API). This project aims to provide a new add-on, implementing a workflow that is similar to that of the **ArmaToolbox**, with improved and extended features and an interface that's more in-line with the design of **Blender**.

## Origins

The project is originally a fork of Alwarren's repository, but in reality, instead of consisting of smaller changes to be merged into the main repository,
it turned into a completely different add-on that reimplements a similar workflow with improved functionality and extended features.

Excerpt from the ArmAToolbox readme:

```txt
Arma Toolbox for Blender
This is a collection of Python scripts for the Blender 3D package
that allows the user to create, import and export unbinarized
Arma Engine .p3d files.
```

## Requirements and Compatibility

- [**Blender** v2.90.0](https://www.blender.org/download/releases/2-90/) or higher
- [**Arma 3 Tools**](https://store.steampowered.com/app/233800/Arma_3_Tools/) (optional for some features to work)

The add-on is developed on **Blender** v2.90.0 for convenience reasons, which also has the side effect that
it supports older versions, not just the latest releases. The add-on is tested on newer releases regardless.
If a new release of **Blender** in the future renders it impossible to keep the add-on compatible with both old,
and new releases, support will be dropped for legacy versions in favor of the new API.

The range of **Blender** releases tested for compatibility is indicated in the changelog entry of each packed release of the add-on.

## License

As inherited from the **ArmAToolbox**, the **Arma 3 Object Builder** add-on is released under the GNU General Public License version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR  PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see the [GNU licenses](http://www.gnu.org/licenses/).

Files created using this software are not covered by this license.
