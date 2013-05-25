from geofu import collection

pts = collection("test_data/at_shelters.shp", "r")

# reproject to US National Atlas
#states = state_centroids.reproject(2163)
pts = polys.centroid()

import ipdb; ipdb.set_trace()

# buffer the points by 5000 meters
#point_buffers = points_proj.buffer(5000)

# print point_buffers.geojson(indent=2)[:200]
# print "And again..."
# print point_buffers.geojson(indent=2)[:200]

#print point_buffers.validate_geojson()
# print point_buffers.mapfart(display=True)


# TODO
#print point_buffers.save()
#print point_buffers.render() # png, svg, geojson/html
#print point_buffers.summary()
