import os
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements():
    return [i.strip() for i in open("requirements.txt").readlines()
            if not i.startswith("http")]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="geofu",
    version="0.0.1",
    author="Matthew Perry",
    author_email="perrygeo@gmail.com",
    description=("Like kungfu, only with geographic data"),
    license="BSD",
    keywords="gis geospatial geographic",
    url="http://perrygeo.net",
    package_dir={'': 'src'},
    packages=['geofu'],
    long_description=read('README.md'),
    install_requires=requirements(),
    scripts=['scripts/geofu'],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
