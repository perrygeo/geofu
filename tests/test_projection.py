# test zonal stats
from geofu.utils import guess_crs

def test_crs_property(points, points_noproj):
	assert points.crs
	assert points_noproj.crs is None  # projection is undefined

def test_assign_crs(points, points_noproj):
	points_noproj.assign_crs(points.crs)
	assert points_noproj.crs == points.crs

def test_guess_crs(points, points_noproj):
	the_crs = points.crs
	assert guess_crs(points) == the_crs
	assert guess_crs(points.crs) == the_crs
	assert guess_crs(points_noproj) is None
	assert guess_crs(4326) == {u'init': u'epsg:4326', u'no_defs': True}  # TODO expand epsg defs
	assert guess_crs("+datum=WGS84 +nodefs +proj=longlat") == \
	                 {u'datum': u'WGS84', u'proj': u'longlat'}

def test_reproject_points(points):
	d = points.reproject(4326)
	assert d.crs == {u'datum': u'WGS84', u'no_defs': True, u'proj': u'longlat'}

def test_reproject_poly(polygons):
	d = polygons.reproject(4326)
	assert d.crs == {u'datum': u'WGS84', u'no_defs': True, u'proj': u'longlat'}
