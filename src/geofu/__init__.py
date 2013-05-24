# -*- coding: utf-8 -*-
"""
geofu
"""

from fiona.collection import Collection as FionaCollection
from shapely.geometry import mapping, shape
from pyproj import Proj, transform


class GeofuCollection(FionaCollection):
    """
    Geofu collection extends fiona collection
    """

    def mapfart(self):
        import requests
        mapfart_url = 'http://mapfart.com/api/fart'
        res = requests.post(mapfart_url, data=self.geojson())
        if res.status_code != 200:
            raise Exception("Mapfart returned a %d" % res.status_code)
        return res.text.strip()

    def validate_geojson(self):
        import requests
        validate_endpoint = 'http://geojsonlint.com/validate'
        res = requests.post(validate_endpoint, data=self.geojson())
        return res.json()

    def geojson(self, indent=None):
        import json
        fc = {
            "type": "FeatureCollection",
            "features": [dict(type='Feature', **x) for x in list(self)],
            "crs": None  # TODO
        }
        return json.dumps(fc, indent=indent)

    def tempds(self, opname):
        return "/tmp/%s_%s.shp" % (self.name, opname)

    def buffer(self, distance):
        out_schema = self.schema.copy()
        out_schema['geometry'] = 'Polygon'

        tempds = self.tempds("buffer_%s" % distance)
        with collection(tempds, "w",
                        "ESRI Shapefile", out_schema) as out_collection:
            for in_feature in self:
                out_feature = in_feature.copy()
                out_feature['geometry'] = mapping(
                    shape(in_feature['geometry']).buffer(distance)
                )
                out_collection.write(out_feature)

        return collection(tempds, "r")

    def reproject(self, crsish):
        in_proj = Proj(self.crs)
        out_schema = self.schema.copy()
        out_crs = guess_crs(crsish)

        tmpds = self.tempds("reproject_%s" % crsish)
        with collection(tmpds, "w", "ESRI Shapefile",
                        out_schema, crs=out_crs) as out_collection:
            out_proj = Proj(out_collection.crs)
            for in_feature in self:

                out_feature = in_feature.copy()
                x2, y2 = transform(in_proj, out_proj,
                                   *in_feature['geometry']['coordinates'])
                out_feature['geometry']['coordinates'] = x2, y2
                out_collection.write(out_feature)

        return collection(tmpds, "r")


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
    from fiona import crs

    try:
        #is it a crs object itself?
        if thing.keys() and \
           set(thing.keys()).issubset(set(crs.all_proj_keys)):
            return thing
    except AttributeError:
        pass

    try:
        # is it a collection or something else with a crs attr?
        return thing.crs
    except AttributeError:
        pass

    try:
        # if it's an int, use an epsg code
        epsg = int(thing)
        return crs.from_epsg(epsg)
    except ValueError:
        pass

    # finally try a string parser
    return crs.from_string(thing)
