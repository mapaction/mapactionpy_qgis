import subprocess
from setuptools import setup, find_packages
from os import path, environ

_base_version = '0.2.4'
_root_dir = path.abspath(path.dirname(__file__))


def readme():
    with open(path.join(_root_dir, 'README.rst')) as f:
        return f.read()


# See https://packaging.python.org/guides/single-sourcing-package-version/
# This uses method 4 on this list combined with other methods.
def _get_version_number():
    travis_build = environ.get('TRAVIS_BUILD_NUMBER')
    travis_tag = environ.get('TRAVIS_TAG')

    if travis_build:
        if travis_tag:
            version = travis_tag
        else:
            version = '{}.dev{}'.format(_base_version, travis_build)

        with open(path.join(_root_dir, 'VERSION'), 'w') as version_file:
            version_file.write(version.strip())

    else:
        try:
            ver = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
            version = '{}+local.{}'.format(_base_version, ver.decode('ascii').strip())
        except Exception:
            with open(path.join(_root_dir, 'VERSION')) as version_file:
                version = version_file.read().strip()

    return version


setup(name='mapactionpy_qgis',
      version=_get_version_number(),
      description='Used to drive QGIS',
      long_description=readme(),
      long_description_content_type="text/x-rst",
      url='http://github.com/mapaction/mapactionpy_qgis',
      author='MapAction',
      author_email='github@mapaction.com',
      license='GPL3',
      packages=find_packages(),
      install_requires=[
          'mapactionpy_controller'
      ],
      test_suite='unittest',
      tests_require=['unittest'],
      zip_safe=False,
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent",
      ])
