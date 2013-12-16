
# This project has been abandoned
##  The concept is very similar to geopandas which has a better implementation and more momentum. So I'll move the best ideas to [my geopandas fork](https://github.com/perrygeo/geopandas).



Geofu aims to provide a python module that works at the level of abstraction that is common in day-to-day GIS and spatial analysis tasks.

IOW, the goal is to think about operations on _layers_ rather than dig deep into the features. All the details of _how_ the operation is done is hidden behind a clean API. If you have to iterate through the features or otherwise get down to lower-level constructs, you probably shouldn't be using it.

The goal is to wrap the functionality of great libraries like 
GEOS, OGR and GDAL with high level methods 
so you can do cool stuff like:

```
from geofu import load

regions = load("test_data/EcoregionVariants6_ORWA.shp")
points = load("test_data/test_pts.shp")

# points are in latlon but regions are in ?? Make sure they match...
points_proj = points.reproject(regions.crs)

# buffer the points by 5000 meters
point_buffers = points_proj.buffer(5000)

# Look at the geojson
print point_buffers.geojson(indent=2)

# Perform an intersection
region_point_int = regions.intersection(point_buffers)

region_point_int.render_png()

```

This is very very pre-Alpha at this point. A bare-bones proof of concept. You've been warned.
