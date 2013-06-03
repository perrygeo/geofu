#!/bin/bash
# Provision base software required for running geofu

apt-get install -y python-software-properties
add-apt-repository -y ppa:mapnik/v2.1.0
add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
apt-get update

apt-get install -y libgdal-dev gdal-bin python-gdal python-pip \
                   libmapnik mapnik-utils python-mapnik \
                   libspatialindex-dev libspatialindex1 \
                   build-essential git atop python-dev python-dateutil

pip install -r requirements.txt

cd /usr/local/src/geofu
python setup.py develop
