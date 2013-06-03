import os
import geofu
import pytest


def test_save_shp(polygons):
    tempds = "/tmp/test.shp"
    d = polygons.save(tempds)
    assert os.path.exists(d.path)
    assert d.path == tempds


def test_load_nonexistent():
    DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    with pytest.raises(IOError):
        d = geofu.load(os.path.join(DATA, "THISFILEDOESNOTEXISTANYWHERE.shp"))


def test_repr(points, raster):
    assert "Layer" in points.__repr__()
    assert "points.shp" in points.__repr__()
    assert "Band" in raster.__repr__()


def test_tempds(points):
	assert points.tempds("buffer").endswith("points_buffer.shp")
	randds = points.tempds()
	assert "points_" in randds
	assert randds.endswith(".shp")
