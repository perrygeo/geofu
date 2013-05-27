from geofu import load

d1 = load("test_data/union_test/states.shp")
d2 = load("test_data/testname_buffer.shp")

d12 = d1.intersection(d2)
d12.render_png(show=True)
print d12

d12 = d1.identity(d2)
d12.render_png(show=True)
print d12

d12 = d1.union(d2)
d12.render_png(show=True)
print d12
