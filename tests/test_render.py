import os

def test_render_png(points, lines, polygons):
	assert os.path.exists(points.render_png())
	assert os.path.exists(lines.render_png())
	assert os.path.exists(polygons.render_png())
	# TODO how to test for graphic output?
	# TODO test for image size, etc

