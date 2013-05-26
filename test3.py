from matplotlib import pyplot
from shapely.geometry import LineString, Point
from descartes import PolygonPatch
import random

BLUE = "#4444FF"
GRAY = "#AAAAAA"
SIZE = (10, 9)
label_hits = ["centroid"]

def plot_poly(ax, ob, label, c=BLUE):
    if label not in label_hits:
        patch1 = PolygonPatch(ob, fc=c, ec="#444444", alpha=1, zorder=2, label=label)
        label_hits.append(label)
    else:
        patch1 = PolygonPatch(ob, fc=c, ec="#444444", alpha=1, zorder=2)

    ax.add_patch(patch1)

fig = pyplot.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

print "creating layers..."
line1 = LineString([(0, 0), (20, 10), (0, 20), (20, 20), (30, 10), (10, 0)])
line2 = LineString([(20, 0), (40, 10), (20, 20), (50, 20), (50, 10), (30, 0)])
line3 = LineString([(10, 20), (30, 30), (10, 40), (30, 40), (40, 30), (20, 20)])

layer1 = [line1.buffer(random.uniform(1,3)), line2.buffer(random.uniform(1,3)), line3.buffer(random.uniform(1,3))] 
layer2 = [Point((random.uniform(0,40), random.uniform(0,40))).buffer(random.uniform(0.2,2)) for x in range(150)]

######################
from shapely.ops import unary_union

print "unioning rings"
rings = []
for layer in [layer1, layer2]:
    for poly in layer:
        rings.append(poly.exterior)
        rings.extend(poly.interiors)

mm = unary_union(rings)

print "polygonize rings"
from shapely.ops import polygonize
newpolys = polygonize(mm)

print "determine spatial relationship and plot new polys"
for p in newpolys:
    cent = p.representative_point()

    # Test intersection with original polys 
    # and transfer attrs
    # this is where the exponential performance decay hits ya
    # need a way to query with spatial index	
    layer1_hit = False
    layer2_hit = False
    for poly in layer1:
        if cent.intersects(poly):
            layer1_hit = True
            # TODO record WHICH poly was hit and collect attrs
            break  # use the first one
    for poly in layer2:
        if cent.intersects(poly):
            layer2_hit = True
            # TODO record WHICH poly was hit and collect attrs
            break  # use the first one
    #print "\t%s\t\tlayer1: %s\tlayer2: %s" % (cent, layer1_hit, layer2_hit)
    # TODO write out p with attrs gathered from ^^

    if layer1_hit and layer2_hit:  # intersection
        color = "#FF4444"
        label = "intersection"
    elif layer1_hit and not layer2_hit:   # identity layer1
        color = "#44FF44"
        label = "identity 1"
    elif not layer1_hit and layer2_hit:   # identity layer2
        color = "#4444FF"
        label = "identity 2"
    else:  # not even in the union
        color = "#AAAAAA"
        label = "null"
    # union = intersection + identity1 + identity2
    # sym diff = identity1 + identity2

    plot_poly(ax, p, label, color)
    plot_poly(ax, cent.buffer(0.05), "centroid", "#000000")

#####################

ax.set_title('Polygon sets')
ax.legend()
xrange = [-2, 58]
yrange = [-2, 42]
ax.set_xlim(*xrange)
ax.set_xticks(range(*xrange) + [xrange[-1]])
ax.set_ylim(*yrange)
ax.set_yticks(range(*yrange) + [yrange[-1]])
ax.set_aspect(1)
pyplot.show()
