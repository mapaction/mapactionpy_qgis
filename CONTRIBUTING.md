# Overview

The plugin works in tandem with the controller to automate data checking and map production. The controller provides much of the common core, vendor-neutral functionality with no dependencies on individual GIS APIs, whist the plugins, provide vendor-specific use of GIS APIs.

# Interface with the Controller

Much of the general functionality for finding and checking the available data and then producing maps is provided by the `mapactionpy_controller` module.

The principle interface for plugins is to subclass `BaseRunnerPlugin` and providing implementations of the various methods which raise  `NotImplementedError`:
https://github.com/mapaction/mapactionpy_controller/blob/master/mapactionpy_controller/plugin_base.py

The critical method is `build_project_files`. The controller will pass a parameter kwargs['state'] which is a MapRecipe object. At this point, the object resembles this [example JSON representation](mapactionpy_qgis/tests/example_files/MA9001-v16-example-overview-map-post-controller.json). The method should perform most of the functions delegated to the plugin.

The de-facto reference implenmentation is the [`mapactionpy_arcmap`](https://github.com/mapaction/mapactionpy_controller) module.

Whilst, in theory, it would be possible to produce a basic plugin by "just" subclassing `BaseRunnerPlugin`, a more thorough implementation may also make changes to the controller module and its workflow itself.

# Tasks delegated to the plugin

The remaining development in QGIS needs a component that will take the [recipe object above](mapactionpy_qgis/tests/example_files/MA9001-v16-example-overview-map-post-controller.json) this specification and turn it into a QGIS project, or series of projects, which reference the source data and the files, and include appropriate Print Layouts. We’ll need components which:

* Creates a new QGIS project
* Load the referenced data
* Apply the appropriate styles
* Create Print Layouts
* Set the QGIS variables which populate the template marginalia
* Export the Print Layouts along with relevant metadata for onward distribution.

The result will be a module that uses the QGIS Python API to drive this production pipeline. It does not need to be a plugin for QGIS itself. There is scope to explore whether there is potential functional overlap with [`mapexport-qgis3`](https://github.com/mapaction/mapexport-qgis3). "mapexport-qgis3" is an interactive QGIS plugin that exports maps, data and their metadata in a manner ready for [import into CKAN](https://github.com/aptivate/ckanext-mapactionimporter). In particular, it would be valuable to explore potential code-sharing/re-use between the projects.

Non-programming tasks required to support this development:

* Conversion of Arc Layer files to QML (probably using SLYR)
* QGIS Templates in line with Arc Templates (using QGIS Template scripts)

