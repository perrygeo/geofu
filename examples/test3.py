from matplotlib import pyplot
from descartes import PolygonPatch

label_hits = ["centroid"]


def plot_poly(ax, ob, label, c="#ffff00"):
    if label not in label_hits:
        patch1 = PolygonPatch(ob, fc=c, ec=c, alpha=0.8, zorder=2, label=label)
        label_hits.append(label)
    else:
        patch1 = PolygonPatch(ob, fc=c, ec=c, alpha=0.8, zorder=2)

    ax.add_patch(patch1)


fig = pyplot.figure(1, figsize=(9, 8), dpi=90)
ax = fig.add_subplot(111)

print "reading two polygon layers..."
from fiona import collection
#coll1 = collection("test_data/union_test/major_urban_areas.shp")
coll1 = collection("test_data/union_test/states.shp")
coll2 = collection("test_data/testname_buffer.shp") # buffered state centroids

######################
from shapely.geometry import shape
from shapely.ops import unary_union, polygonize

from rtree import index
idx1 = index.Index()
idx2 = index.Index()

print "unioning rings"
layer1 = {}  # id: shapely geom, properties dict
layer2 = {}  # id: shapely geom, properties dict
rings1 = []
rings2 = []

print "\tcollection1"
for rec in coll1:
    geom = shape(rec['geometry'])

    # if rec['properties']['STATE_NAME'] == 'Massachusetts':
    #     pass  # continue to exclude Mass
    # else:
    #     pass  # continue to exclude everything but Mass

    rid = int(rec['id'])
    layer1[rid] = (geom, rec['properties'])
    idx1.insert(rid, geom.bounds)
    if hasattr(geom, 'geoms'):
        for poly in geom.geoms:  # if it's a multipolygon
            if not poly.is_valid:
                print "***** Geometry from layer1 is not valid, fixing by buffer 0"
                poly = poly.buffer(0)
            rings1.append(poly.exterior)
            rings1.extend(poly.interiors)
    else:
        if not geom.is_valid:
            print "***** Geometry from layer1 is not valid, fixing by buffer 0"
            geom = geom.buffer(0)
        rings1.append(geom.exterior)
        rings1.extend(geom.interiors)


print "\tcollection2"
for rec in coll2:
    geom = shape(rec['geometry'])

    rid = int(rec['id'])
    layer2[rid] = (geom, rec['properties'])
    idx2.insert(rid, geom.bounds)

    if hasattr(geom, 'geoms'):
        for poly in geom.geoms:  # multipolygon
            if not poly.is_valid:
                print "***** Geometry from layer2 is not valid, fixing by buffer 0"
                poly = poly.buffer(0)
            rings2.append(poly.exterior)
            rings2.extend(poly.interiors)
    else:
        if not geom.is_valid:
            print "***** Geometry from layer2 is not valid, fixing by buffer 0"
            geom = geom.buffer(0)
        rings2.append(geom.exterior)
        rings2.extend(geom.interiors)

#print "\t", len([x for x in rings if not x.is_valid]), "invalid rings"
#rings = [x for x in rings if x.is_valid]

from shapely.geometry import MultiLineString

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

print "determine spatial relationship and plot new polys"
for newpoly in newpolys:
    cent = newpoly.representative_point()

    # Test intersection with original polys
    layer1_hit = False
    layer2_hit = False
    candidates1 = list(idx1.intersection(cent.bounds))
    candidates2 = list(idx2.intersection(cent.bounds))

    for cand in candidates1:
        if cent.intersects(layer1[cand][0]):
            layer1_hit = True
            # prop1 = layer1[cand][1]  # properties
            break

    for cand in candidates2:
        if cent.intersects(layer2[cand][0]):
            layer2_hit = True
            # prop2 = layer2[cand][1]  # properties
            break

    if layer1_hit and layer2_hit:  # intersection
        color = "#FF4444"
        label = "intersection"
    elif layer1_hit and not layer2_hit:
        color = "#44FF44"
        label = "layer 1 only"
    elif not layer1_hit and layer2_hit: 
        color = "#4444FF"
        label = "layer 2 only"
    else:  # not even in the union
        color = "#AAAAAA"
        label = "null"

    # TODO write out newpoly with attrs gathered from prop1 & prop2
    # output based on type of overlay
    #   union = intersection + only1 + only2
    #   sym diff = only1 + only2
    #   indentity1 = only1 + intersection
    #   indentity2 = only1 + intersection
    #   intersection = intersection

#####################

    plot_poly(ax, newpoly, label, color)
    plot_poly(ax, cent.buffer(0.03), "centroid", "#000000")


ax.set_title('Polygon sets')
ax.legend(loc=4)
xrange = [-87, -66]
yrange = [30, 48]
ax.set_xlim(*xrange)
ax.set_xticks(range(*xrange) + [xrange[-1]])
ax.set_ylim(*yrange)
ax.set_yticks(range(*yrange) + [yrange[-1]])
ax.set_aspect(1)
pyplot.show()
