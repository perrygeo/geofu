Not sure what this is yet or why it's called geofu...

The goal is to extend fiona collections with high level methods 
so you can do cool stuff like:

```
from geofu import collection

regions = collection("test_data/EcoregionVariants6_ORWA.shp", "r")
points = collection("test_data/test_pts.shp", "r")

# points are in latlon but regions are in albers! Make sure they match...
points_proj = points.reproject(regions.crs)

# buffer the points by 5000 meters
point_buffers = points_proj.buffer(5000)
```
