# -*- coding: utf-8 -*-
"""
geofu
"""
from geofu._layer import Layer
from geofu._band import Band
from osgeo import ogr, gdal
import os


def load(path, layernum=0):
    path = os.path.abspath(path)
    obj = None
    rds = gdal.Open(path)
    if rds:
        obj = Band(path)

    vds = ogr.Open(path)
    if vds:
        name = vds.GetLayer(layernum).GetName()
        obj = Layer(path, name)

    rds = None
    vds = None
    if not obj:
        raise IOError("Did not recognize %s as a vector or raster dataset")

    return obj
