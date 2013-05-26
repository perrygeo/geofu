from matplotlib import pyplot
from shapely.geometry import LineString
from descartes import PolygonPatch
import random

#from figures import SIZE, BLUE, GRAY
BLUE = "#4444FF"
GRAY = "#AAAAAA"
SIZE = (6, 6)

def plot_line(ax, ob, i=None):
    x, y = ob.xy
    r = lambda: random.randint(0, 255)
    c = '#%02X%02X%02X' % (r(), r(), r())
    ax.plot(x, y, color=c, linewidth=5, solid_capstyle='round', zorder=1)

def plot_poly(ax, ob, ec=BLUE):
    r = lambda: random.randint(0, 255)
    c = '#%02X%02X%02X' % (r(), r(), r())
    patch1 = PolygonPatch(ob, fc=c, ec=ec, alpha=1, zorder=2)
    ax.add_patch(patch1)

line1 = LineString([(0, 0), (2, 1), (0, 2), (2, 2), (3, 1), (1, 0)])
line2 = LineString([(1, 0), (3, 1), (1, 2), (3, 2), (4, 1), (2, 0)])

poly1 = line1.buffer(0.2)
poly2 = line2.buffer(0.3)

######################
from shapely.ops import unary_union
rings = [poly1.exterior, poly2.exterior] + list(poly1.interiors) + list(poly2.interiors)
mm = unary_union(rings)

from shapely.ops import polygonize
allpolys = polygonize(mm)


fig = pyplot.figure(1, figsize=SIZE, dpi=90)

ax = fig.add_subplot(111)

#plot_line(ax, line1)
# for lineseg in mm:
#     plot_line(ax, lineseg, 1)

centroids = []
for p in allpolys:
    centroids.append(p.representative_point())
    plot_poly(ax, p)

for cent in centroids:
	plot_poly(ax, cent.buffer(0.05), "#000000")
    # this is where the exponential performance decay hits ya
    # need a way to query with spatial index	
    # for poly in input polys:
    #    test intersection
	print cent, cent.intersects(poly1), cent.intersects(poly2)


#####################

# patch1 = PolygonPatch(poly1, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
# ax.add_patch(patch1)

# patch2a = PolygonPatch(poly2, fc=GRAY, ec=GRAY, alpha=0.5, zorder=1)
# ax.add_patch(patch2a)

ax.set_title('a) dilation')

xrange = [-1, 5]
yrange = [-1, 5]
ax.set_xlim(*xrange)
ax.set_xticks(range(*xrange) + [xrange[-1]])
ax.set_ylim(*yrange)
ax.set_yticks(range(*yrange) + [yrange[-1]])
ax.set_aspect(1)



pyplot.show()

