# -*- coding: utf-8 -*-
"""
geofu
"""
from geofu._layer import Layer
from geofu._band import Band
from osgeo import ogr, gdal


def load(path):
    obj = None
    rds = gdal.Open(path)
    if rds:
        obj = Band(path)

    vds = ogr.Open(path)
    if vds:
        obj = Layer(path)

    rds = None
    vds = None
    if not obj:
        raise Exception("Did not recognize %s as a vector or raster dataset")

    return obj
