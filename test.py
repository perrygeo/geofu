from geofu import collection

points = collection("test_data/test_pts.shp", "r")

# reproject to utm zone 10 nad83, epsg code 26910
points_proj = points.reproject(26910)

# buffer the points by 5000 meters
point_buffers = points_proj.buffer(5000)

#print point_buffers.geojson(indent=2)
#print point_buffers.validate_geojson()
#print point_buffers.mapfart()

# TODO
#print point_buffers.save()
#print point_buffers.render() # png, svg, geojson/html
#print point_buffers.summary()
