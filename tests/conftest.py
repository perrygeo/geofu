import pytest
import geofu
import os
import sys
import logging

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


@pytest.fixture
def points():
    return geofu.load(os.path.join(DATA, "points.shp"))


@pytest.fixture
def lines():
    return geofu.load(os.path.join(DATA, "lines.shp"))


@pytest.fixture
def polygons():
    return geofu.load(os.path.join(DATA, "polygons.shp"))


@pytest.fixture
def raster():
    return geofu.load(os.path.join(DATA, "slope.tif"))
