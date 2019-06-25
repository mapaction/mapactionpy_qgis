from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='mapactionpy_qgis',
      version='0.1',
      description='Used to drive QGIS',
      url='http://github.com/mapaction/mapactionpy_qgis',
      author='MapAction',
      author_email='github@mapaction.com',
      license='GPL3',
      packages=['mapactionpy_qgis'],
	  test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)