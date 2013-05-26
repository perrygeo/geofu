# -*- coding: utf-8 -*-
"""
geofu
"""

from shapely.geometry import mapping, shape
from pyproj import Proj, transform
from fiona import collection
from PIL import Image
import requests
import json
import random
import string
import os
from fiona import crs
import fiona
import mapnik


class Layer():

    def __init__(self, path):
        self.path = path
        self.name = "testname"

    def __repr__(self):
        return "<geofu.Layer at `%s`>" % self.path

    @property
    def crs(self):
        return self.collection().crs

    def collection(self, *args, **kwargs):
        """
        a fiona collection for the layer
        """
        return collection(self.path, *args, **kwargs)

    def mapfart(self, show=False, download=False):
        mapfart_url = 'http://mapfart.com/api/fart'
        res = requests.post(mapfart_url, data=self.geojson())
        if res.status_code != 200:
            raise Exception("Mapfart returned a %d" % res.status_code)
        url = res.text.strip()

        if not download and not show:
            return url

        res = requests.get(url)
        if res.status_code == 200:
            filename = self.tempds(ext="png")
            with open(filename, 'wb') as fh:
                for chunk in res.iter_content(1024):
                    fh.write(chunk)
            if show:
                im = Image.open(filename)
                im.show()
            return filename
        else:
            raise Exception("Mapfart returned a %d" % res.status_code)

    def render_png(self, show=False):
        m = mapnik.Map(600, 300)
        m.background = mapnik.Color('white')
        s = mapnik.Style()
        r = mapnik.Rule()

        if "point" in self.collection().schema['geometry'].lower():
            point_symbolizer = mapnik.PointSymbolizer()
            r.symbols.append(point_symbolizer)
        else:
            polygon_symbolizer = mapnik.PolygonSymbolizer(
                mapnik.Color('#f2eff9')
            )
            r.symbols.append(polygon_symbolizer)

            line_symbolizer = mapnik.LineSymbolizer(
                mapnik.Color('rgb(50%,50%,50%)'), 0.8
            )
            r.symbols.append(line_symbolizer)

        s.rules.append(r)
        m.append_style('My Style', s)
        ds = mapnik.Shapefile(file=self.path)
        layer = mapnik.Layer('world')
        layer.datasource = ds
        layer.styles.append('My Style')
        m.layers.append(layer)
        m.zoom_all()
        outfile = '/tmp/world.png'
        mapnik.render_to_file(m, outfile, 'png')
        if show:
            im = Image.open(outfile)
            im.show()
        return outfile

    def validate_geojson(self):
        validate_endpoint = 'http://geojsonlint.com/validate'
        res = requests.post(validate_endpoint, data=self.geojson())
        return res.json()

    def geojson(self, indent=None):
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
            opname = ''.join(random.choice(
                                string.ascii_uppercase + string.digits)
                             for x in range(10)
            )

        return "/tmp/%s_%s.%s" % (self.name, opname, ext)

    def apply_shapely(self, method, args=None, call=True, out_geomtype=None,
                      **kwargs):
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
    if not os.path.exists(path):
        raise IOError("no such file or directory: %r" % path)
    c = Layer(path)
    return c


def guess_crs(thing):

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
