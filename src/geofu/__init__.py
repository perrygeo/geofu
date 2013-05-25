# -*- coding: utf-8 -*-
"""
geofu
"""

from shapely.geometry import mapping, shape
from pyproj import Proj, transform


class Layer():

    def __init__(self, path):
        self.path = path
        self.name = "testname"

    @property
    def crs(self):
        return self.collection().crs

    def collection(self, *args, **kwargs):
        """
        a fiona collection for the layer
        """
        from fiona import collection
        return collection(self.path, *args, **kwargs)

    def mapfart(self, show=False, url_only=False):
        import requests
        mapfart_url = 'http://mapfart.com/api/fart'
        res = requests.post(mapfart_url, data=self.geojson())
        if res.status_code != 200:
            raise Exception("Mapfart returned a %d" % res.status_code)
        url = res.text.strip()
        if url_only:
            return url
        res = requests.get(url)
        if res.status_code == 200:
            filename = self.tempds(ext="png")
            with open(filename, 'wb') as fh:
                for chunk in res.iter_content(1024):
                    fh.write(chunk)
            if show:
                from PIL import Image
                im = Image.open(filename)
                im.show()
            return filename
        else:
            raise Exception("Mapfart returned a %d" % res.status_code)

    def validate_geojson(self):
        import requests
        validate_endpoint = 'http://geojsonlint.com/validate'
        res = requests.post(validate_endpoint, data=self.geojson())
        return res.json()

    def geojson(self, indent=None):
        import json
        coll = self.collection()
        fc = {
            "type": "FeatureCollection",
            "features": [dict(type='Feature', **x)
                         for x in list(coll)],
            "crs": None  # TODO
        }
        del coll
        return json.dumps(fc, indent=indent)

    def tempds(self, opname=None, ext="shp"):
        if not opname:
            import random
            import string
            opname = ''.join(random.choice(
                                string.ascii_uppercase + string.digits)
                             for x in range(10)
            )

        return "/tmp/%s_%s.%s" % (self.name, opname, ext)

    def apply_shapely(self, method, args=None, call=True, out_geomtype=None,
                      **kwargs):
        import fiona
        coll = self.collection()
        out_schema = coll.schema.copy()
        if not args:
            args = []
        if out_geomtype:
            out_schema['geometry'] = out_geomtype

        tempds = self.tempds(method)
        with fiona.collection(tempds, "w",
                        "ESRI Shapefile", out_schema) as out_collection:
            for in_feature in coll:
                out_feature = in_feature.copy()
                if call:
                    geom = mapping(
                        getattr(shape(in_feature['geometry']), method)(*args, **kwargs)
                    )
                else:
                    # it's not a method, it's a property
                    geom = mapping(
                        getattr(shape(in_feature['geometry']), method)
                    )

                out_feature['geometry'] = geom
                out_collection.write(out_feature)
        return Layer(tempds)

    def centroid(self):
        return self.apply_shapely("centroid", call=False, out_geomtype="Point")

    def simplify(self, tolerance):
        return self.apply_shapely("simplify", [tolerance])

    def buffer(self, distance):
        return self.apply_shapely("buffer", [distance], out_geomtype="Polygon")

    def reproject(self, crsish):
        import fiona
        in_proj = Proj(self.crs)
        coll = self.collection()
        out_schema = coll.schema.copy()
        out_crs = guess_crs(crsish)

        tmpds = self.tempds("reproject_%s" % crsish)
        with fiona.collection(tmpds, "w", "ESRI Shapefile",
                        out_schema, crs=out_crs) as out_collection:
            out_proj = Proj(out_collection.crs)
            for in_feature in coll:

                out_feature = in_feature.copy()
                x2, y2 = transform(in_proj, out_proj,
                                   *in_feature['geometry']['coordinates'])
                out_feature['geometry']['coordinates'] = x2, y2
                out_collection.write(out_feature)

        return Layer(tmpds)


def load(path):
    import os
    if not os.path.exists(path):
        raise IOError("no such file or directory: %r" % path)
    c = Layer(path)
    return c


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
