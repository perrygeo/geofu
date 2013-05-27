from geofu import load
print load("test_data/at_shelters.shp")\
    .reproject(2163).buffer(21000).reproject(4326)\
    .save("test_data/woot.shp")\
    .render_png(show=True)
