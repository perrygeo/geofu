import json

def test_dict(points):
	d = points.as_dict()
	assert d['features']
	assert d['type'] == 'FeatureCollection'

def test_geojson(points):
    assert points.geojson()
    