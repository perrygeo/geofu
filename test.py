from geofu import collection

points = collection("test_data/test_pts.shp", "r")

points_proj = points.reproject({u'lon_0': -120, u'ellps': u'GRS80',
    u'datum': u'NAD83', u'y_0': 0, u'no_defs': True, u'proj': u'aea', u'x_0': 600000,
    u'units': u'm', u'lat_2': 48, u'lat_1': 43, u'lat_0': 34})

# buffer the points by 5000 meters
point_buffers = points_proj.buffer(5000)

print point_buffers
print 
print "Try `ogr2geojson ____ | mapfart`"

