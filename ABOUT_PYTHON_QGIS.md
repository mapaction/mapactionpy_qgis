# Why is this required?
It is likely that there are multiple python installations on your computer. These may have been installed indepenantly, or as a component of another piece of software. For example ArcMap, QGIS, ArcGIS Pro, GIMP, Inkscape, pgAdmin, Anaconda and Visual Studio all install their own instance of Python. In some cases a single software suite may legitimately install multiple instances of python (OSGeo4W and Visual Studio are two such examples)

Unfortuantly this can be futher complicated by the fact that there are a number of ways in which that a python instance can (attempt to) claim to be the "one-true" default python. Without care this can sometimes, cause problems if there are competing, incomptable claims to be the default python.

_Therefore for any non-MapAction computer there are inumerable possible combinations of python installations and configurations - we cannot possibly know what they are._

Most of the problems with installing the MapAction python based software which are reported can be traced back to a failure to correctly indentify the relevant python environment on the target computer.

_Therefore before installing any of the MapAction python based software you must ensure that you have identified the relevant python instance._

This page offers _guidance_ on how to identify and confirm that you have the correct python instance. For QGIS or ArcMap related python instances it will depend on on _how_ either QGIS or ArcMap was installed on your computer and the particular options choosen at install time, hence you will need to interpret this guidance as appropriate for your computer.


# QGIS on Windows
Note* On Windows QGIS tend to wrap up their python instance in a batch file (.bat). This set all of the environment varibable and paths correctly. Use the batch file - you can pass parameters exactly as you would a regular python executable. There will probably be a `python.exe` file in the same directory - but don't call it directly - as it will not work.

## QGIS on Windows if installed as part of OSGeo4W (or OSGeo4W64)
The table below shows the standard path's depending on the installation options selected. If you used a non-default install location you will need to identify the equivilent path on your computer.

<table class="wrapped"><colgroup><col /><col /></colgroup>
<tbody>
<tr>
<th>Installation option</th>
<th>Default path</th></tr>
<tr>
<td>64bit, standard release</td>
<td><code>C:\OSGeo4w64\bin\python-qgis.bat</code></td></tr>
<tr>
<td>64bit, long term release</td>
<td><code>C:\OSGeo4w64\bin\python-qgis-ltr.bat</code></td></tr>
<tr>
<td>32bit, standard release</td>
<td><code>C:\OSGeo4w\bin\python-qgis.bat</code></td></tr>
<tr>
<td>32bit, long term release</td>
<td><code>C:\OSGeo4w\bin\python-qgis-ltr.bat</code></td></tr></tbody></table>
<h3>QGIS on Windows if installed using the standalone installer</h3>
<em><strong>All details to be confirmed</strong></em>

The table below shows the standard path's depending on the installation options selected. If you used a non-default install location you will need to identify the equivilent path on your computer.

<table class="wrapped"><colgroup><col /><col /></colgroup>
<tbody>
<tr>
<th>Installation option</th>
<th>Default path</th></tr>
<tr>
<td>QGIS v3.4, 32bit</td>
<td><code><code>C:\Program Files (x86)\QGIS 3.4\bin\python-qgis-ltr.bat</code></code></td></tr>
<tr>
<td>QGIS v3.4, 64bit</td>
<td><code>C:\Program Files\QGIS 3.4\bin\python-qgis-ltr.bat</code></td></tr>
<tr>
<td>QGIS v3.12, 32bit</td>
<td><code><code>C:\Program Files (x86)\QGIS 3.12\bin\python-qgis.bat</code></code></td></tr>
<tr>
<td>QGIS v3.12, 64bit</td>
<td><code>C:\Program Files\QGIS 3.12\bin\python-qgis.bat</code></td></tr></tbody></table>

## QGIS on Linux
Typically this will use the system default instance of <code>python3</code>. However you will need to adjust your paths to locate the <code>qgis.core</code> libary using the instructions here:

<a href="https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html#running-custom-applications">https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html#running-custom-applications</a>

## QGIS on Mac
Unknown and untested, but likely to be simular to the process for QGIS on Linux.

## Confirming you have found the right python installation for QGIS
To confirm you have identified the correct location for QGIS try the two command shown below. The example shows the two commands using the correct path on a mapaction laptop. When run on your computer you should see the same output, without any errors:
```
# This command must print out the module name `qgis.core` and return without error
<path/to/your/qgis/python> -c 'import qgis.core; print(qgis.core.__name__)'
qgis.core
```

# References
<a href="https://www.python.org/dev/peps/pep-0397/">https://www.python.org/dev/peps/pep-0397/</a>

<a href="http://testerstories.com/2014/06/multiple-versions-of-python-on-windows/">http://testerstories.com/2014/06/multiple-versions-of-python-on-windows/</a>

<a href="https://www.devdungeon.com/content/python-import-syspath-and-pythonpath-tutorial#toc-5">https://www.devdungeon.com/content/python-import-syspath-and-pythonpath-tutorial#toc-5</a>
