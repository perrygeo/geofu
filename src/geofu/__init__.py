# -*- coding: utf-8 -*-
"""
geofu
"""
__all__ = []
__version__ = "0.0.1"


from fiona.collection import Collection as FionaCollection
from shapely.geometry import mapping, shape
from pyproj import Proj, transform


class GeofuCollection(FionaCollection):
    """
    Geofu collection extends fiona collection
    """

    def buffer(self, distance):
        # from geofu.tools import buffer
        # buffer.buffer(self, *args, **kwargs)
        out_schema = self.schema.copy()
        out_schema['geometry'] = 'Polygon'

        out_shp_path = "/tmp/test.shp"
        with collection(out_shp_path, "w", "ESRI Shapefile", out_schema) as out_collection:
            for in_feature in self:
                out_feature = in_feature.copy()
                out_feature['geometry'] = mapping(
                    shape(in_feature['geometry']).buffer(distance)
                )
                out_collection.write(out_feature)

        return open(out_shp_path, "r")

    def reproject(self, out_crs):
        out_schema = self.schema.copy()

        in_proj = Proj(self.crs)

        #out_crs = guess_crs(crs_like)

        out_shp_path = "/tmp/test2.shp"
        with collection(out_shp_path, "w", "ESRI Shapefile", out_schema, crs=out_crs) as out_collection:
            out_proj = Proj(out_collection.crs)
            for in_feature in self:

                out_feature = in_feature.copy()
                x2, y2 = transform(in_proj, out_proj, *in_feature['geometry']['coordinates'])
                out_feature['geometry']['coordinates'] = x2, y2
                out_collection.write(out_feature)

        return open(out_shp_path, "r")


def open(path, mode='r', driver=None, schema=None, crs=None, encoding=None):
    """
    Open file at ``path`` in ``mode`` "r" (read), "a" (append), or
    "w" (write) and return a ``Collection`` object.

    In write mode, a driver name such as "ESRI Shapefile" or "GPX" (see
    OGR docs or ``ogr2ogr --help`` on the command line) and a schema
    mapping such as:

      {'geometry': 'Point', 'properties': { 'class': 'int', 'label':
      'str', 'value': 'float'}}

    must be provided. A coordinate reference system for collections in
    write mode can be defined by the ``crs`` parameter. It takes Proj4
    style mappings like

      {'proj': 'longlat', 'ellps': 'WGS84', 'datum': 'WGS84',
       'no_defs': True}

    The drivers used by Fiona will try to detect the encoding of data
    files. If they fail, you may provide the proper ``encoding``, such as
    'Windows-1252' for the Natural Earth datasets.
    """
    import os
    if mode in ('a', 'r'):
        if not os.path.exists(path):
            raise IOError("no such file or directory: %r" % path)
        c = GeofuCollection(path, mode, encoding=encoding)
    elif mode == 'w':
        c = GeofuCollection(path, mode=mode, crs=crs, driver=driver,
                            schema=schema, encoding=encoding)
    else:
        raise ValueError(
            "mode string must be one of 'r', 'w', or 'a', not %s" % mode)
    return c


collection = open


def guess_crs(thing):
    from fiona.crs import from_epsg

    #is it a crs object itself?
    try:
        # is it a collection or something else with a crs attr?
        return thing.crs
    except AttributeError:
        pass

    print thing
    return from_epsg(thing)

    # TODO what about wkt, .prj file path, proj4 string, pyproj object
    raise AttributeError

