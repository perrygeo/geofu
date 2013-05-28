# -*- coding: utf-8 -*-
"""
geofu._layer.Layer
"""
from shapely.geometry import mapping, shape
from pyproj import Proj, transform
from fiona import collection
from PIL import Image
import requests
import json
import random
import string
import fiona
import mapnik
from shapely.ops import unary_union, polygonize
from shapely.geometry import MultiLineString
from rtree import index
from .utils import guess_crs


class Layer():
    """
    Layer: wrapper class for all vector layers
    """

    def __init__(self, path):
        self.path = path
        self.name = self.collection().name

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

    def intersection(self, layer2):
        return self._overlay(layer2, method="intersection")

    def union(self, layer2):
        return self._overlay(layer2, method="union")

    def identity(self, layer2):
        return self._overlay(layer2, method="identity")

    def _overlay(self, layer2, method):
        assert method in ['union', 'intersection', 'identity']

        idx1 = index.Index()
        idx2 = index.Index()

        # for fast lookup of geometry and properties after spatial index
        # advantage: don't have to reopen ds and seek on disk
        # disadvantage: have to keep everything in memory
        #  {id: (shapely geom, properties dict) }
        # TODO just use the index as the id and just copy the fiona records?
        features1 = {}
        features2 = {}
        rings1 = []
        rings2 = []

        print "gathering LinearRings"
        print "\tself"
        for rec in self.collection():
            geom = shape(rec['geometry'])
            rid = int(rec['id'])
            features1[rid] = (geom, rec['properties'])
            idx1.insert(rid, geom.bounds)
            if hasattr(geom, 'geoms'):
                for poly in geom.geoms:  # if it's a multipolygon
                    if not poly.is_valid:
                        print "\t geom from self layer is not valid," + \
                              " attempting fix by buffer 0"
                        poly = poly.buffer(0)
                    rings1.append(poly.exterior)
                    rings1.extend(poly.interiors)
            else:
                if not geom.is_valid:
                    print "\tgeom from self layer is not valid," + \
                          " attempting fix by buffer 0"
                    geom = geom.buffer(0)
                rings1.append(geom.exterior)
                rings1.extend(geom.interiors)

        print "\tlayer2"
        for rec in layer2.collection():
            geom = shape(rec['geometry'])

            rid = int(rec['id'])
            features2[rid] = (geom, rec['properties'])
            idx2.insert(rid, geom.bounds)

            if hasattr(geom, 'geoms'):
                for poly in geom.geoms:  # multipolygon
                    if not poly.is_valid:
                        print "\t geom from layer2 is not valid," + \
                              " attempting fix by buffer 0"
                        poly = poly.buffer(0)
                    rings2.append(poly.exterior)
                    rings2.extend(poly.interiors)
            else:
                if not geom.is_valid:
                    print "\t geom from layer2 is not valid," + \
                          " attempting fix by buffer 0"
                    geom = geom.buffer(0)
                rings2.append(geom.exterior)
                rings2.extend(geom.interiors)

        #rings = [x for x in rings if x.is_valid]
        mls1 = MultiLineString(rings1)
        mls2 = MultiLineString(rings2)

        try:
            print "calculating union (try the fast unary_union)"
            mm = unary_union([mls1, mls2])
        except:
            print "FAILED"
            print "calculating union again (using the slow a.union(b))"
            mm = mls1.union(mls2)

        print "polygonize rings"
        newpolys = polygonize(mm)

        # print "constructing new schema"
        out_schema = self.collection().schema.copy()
        # TODO polygon geomtype

        layer2_schema_map = {}  # {old: new}
        for key, value in layer2.collection().schema['properties'].items():
            if key not in out_schema['properties']:
                out_schema['properties'][key] = value
                layer2_schema_map[key] = key
            else:
                # try to rename it
                i = 2
                while True:
                    newkey = "%s_%d" % (key, i)
                    if newkey not in out_schema['properties']:
                        out_schema['properties'][newkey] = value
                        layer2_schema_map[key] = newkey 
                        break
                    i += 1 

        tempds = self.tempds(method)
        out_collection = fiona.collection(
            tempds, "w", "ESRI Shapefile", out_schema)

        print "determine spatial relationship and write new polys"
        for fid, newpoly in enumerate(newpolys):
            cent = newpoly.representative_point()

            # Test intersection with original polys
            layer1_hit = False
            layer2_hit = False
            prop1 = None
            prop2 = None
            candidates1 = list(idx1.intersection(cent.bounds))
            candidates2 = list(idx2.intersection(cent.bounds))

            for cand in candidates1:
                if cent.intersects(features1[cand][0]):
                    layer1_hit = True
                    prop1 = features1[cand][1]  # properties
                    break

            for cand in candidates2:
                if cent.intersects(features2[cand][0]):
                    layer2_hit = True
                    prop2 = features2[cand][1]  # properties
                    break

            # determine whether to output based on type of overlay
            hit = False
            if method == "intersection" and (layer1_hit and layer2_hit):
                hit = True
            elif method == "union" and (layer1_hit or layer2_hit):
                hit = True
            elif method == "identity" and ((layer1_hit and layer2_hit) or
                           (layer1_hit and not layer2_hit)):
                hit = True

            if not hit:
                continue

            # write out newpoly with attrs gathered from prop1 & prop2
            if not prop1:
                prop1 = dict.fromkeys(
                    self.collection().schema['properties'].keys(), None)

            if not prop2:
                prop2 = dict.fromkeys(layer2_schema_map.keys(), None)

            newprop = prop1
            for key, value in prop2.items():
                newkey = layer2_schema_map[key]
                newprop[newkey] = value

            out_feature = {
                'id': fid,
                'properties': newprop,
                'geometry': mapping(newpoly)}

            out_collection.write(out_feature)

        out_collection.close()
        return Layer(tempds)

    def render_png(self, show=True):
        #TODO scale dimensions to aspect ratio of data
        m = mapnik.Map(800, 400)
        m.background = mapnik.Color('white')
        s = mapnik.Style()
        r = mapnik.Rule()

        if "point" in self.collection().schema['geometry'].lower():
            point_symbolizer = mapnik.PointSymbolizer()
            r.symbols.append(point_symbolizer)
        else:
            polygon_symbolizer = mapnik.PolygonSymbolizer(
                mapnik.Color('#f2eff9'))
            r.symbols.append(polygon_symbolizer)

            line_symbolizer = mapnik.LineSymbolizer(
                mapnik.Color('rgb(50%,50%,50%)'), 0.8)
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
            return im
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
            "crs": None}  # TODO
        del coll
        return json.dumps(fc, indent=indent)

    def tempds(self, opname=None, ext="shp"):
        if not opname:
            opname = ''.join(random.choice(string.ascii_uppercase +
                             string.digits) for x in range(10))

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
        with fiona.collection(tempds, "w", "ESRI Shapefile",
                              out_schema, crs=self.crs) as out_collection:
            for in_feature in coll:
                out_feature = in_feature.copy()
                if call:
                    geom = mapping(
                        getattr(shape(in_feature['geometry']),
                                method)(*args, **kwargs)
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

                if in_feature['geometry']['type'] == "Polygon":
                    new_coords = []
                    for ring in in_feature['geometry']['coordinates']:
                        x2, y2 = transform(in_proj, out_proj, *zip(*ring))
                        new_coords.append(zip(x2, y2))
                    out_feature['geometry']['coordinates'] = new_coords

                elif in_feature['geometry']['type'] == "Point":
                    x2, y2 = transform(in_proj, out_proj,
                                       *in_feature['geometry']['coordinates'])
                    out_feature['geometry']['coordinates'] = x2, y2

                out_collection.write(out_feature)

        return Layer(tmpds)

    def save(self, filename, driver="ESRI Shapefile"):
        coll = self.collection()
        out_schema = coll.schema.copy()
        with fiona.collection(filename, "w", schema=out_schema,
                              crs=self.crs, driver=driver) as out_collection:
            for in_feature in coll:
                out_collection.write(in_feature.copy())

        return Layer(filename)
