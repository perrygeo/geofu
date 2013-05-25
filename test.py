import geofu

pts = geofu.load("test_data/at_shelters.shp")

# what's out coordinate reference system
print pts.crs

# reproject to US National Atlas
pts = pts.reproject(2163)

# buffer by 5km
ptbuff = pts.buffer(5000)

# use the mapfart.com web service to render it
ptbuff.mapfart(show=True)

# Get it as a fiona collection
print type(ptbuff.collection())

# let's examine the geojson string
print ptbuff.geojson(indent=2)[:200]

# And use geojsonlint.com to validate it
print "Is this geojson valid?", ptbuff.validate_geojson()
