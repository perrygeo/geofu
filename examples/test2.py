import geofu

d = geofu.load("test_data/states.shp")

#d = d.reproject(2163)
d = d.simplify(0.1)

print d.render_png(show=True)
