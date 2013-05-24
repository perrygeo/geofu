import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements():
    return [i.strip() for i in open("requirements.txt").readlines()]

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
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
