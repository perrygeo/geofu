# -*- coding: utf-8 -*-
"""
geofu._layer.Layer
"""
from .utils import guess_crs
from osgeo import gdal


class Band():
    """
    Band: wrapper class for all raster bands
    """

    def __init__(self, path):
        self.path = path
        self.name = "testrasterband"

    def __repr__(self):
        return "<geofu.Band at `%s`>" % self.path
