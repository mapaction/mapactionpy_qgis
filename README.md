
[![Build Status](https://travis-ci.com/mapaction/mapactionpy_qgis.svg?branch=master)](https://travis-ci.com/mapaction/mapactionpy_qgis) 
[![Gitter](https://badges.gitter.im/mapaction/gsoc-ideas.svg)](https://gitter.im/mapaction/gsoc-ideas?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# What is this?

This is a planned plugin for MapChef, which will enable MapChef to produce an automated set of maps based on a recipe. Note it is not a plugin for QGIS itself.


# Why is it needed?

The [MapChef ArcMap plugin](https://github.com/mapaction/mapactionpy_arcmap) can produce a set of base maps, ready for publication or reuse, from a JSON ‘recipe’.

MapAction has access to [SLYR](https://north-road.com/slyr) (which has been generously donated by [North Road](https://north-road.com)). In theory, one approach would be to convert the output of the ArcMap plugin into QGIS-ready products using SLYR. However, this approach retains a dependency on Arc, which partners may not have, and potentially misses an opportunity to complete development in QGIS which - because a significant part of the [MapChef code is intended to be reusable](https://github.com/mapaction/mapactionpy_controller) - should be reasonably straightforward to do.


# Other MapChef plugins (complete and planned)

* ArcMap (in production use)
* Vector tiles (planned)
* ArcGIS Pro (planned)

# Installation

It is necessary to explicitly install both the QGIS plugin and the controller (See [bug #7](https://github.com/mapaction/mapactionpy_qgis/issues/7)). You _must_ identify the appropriate python environment for your QGIS installation. To confirm 

```
# This command must print out the module name `qgis.core` and return without error
<path/to/your/qgis/python> -c 'import qgis.core; print(qgis.core.__name__)'
```

These two commands are required to install the packages:
```
python -m pip install mapactionpy_controller
python -m pip install mapactionpy_qgis
```

# Development

See [CONTRIBUTING.md](CONTRIBUTING.md)
