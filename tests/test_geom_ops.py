# test buffers


def test_point_buffer(points):
    ptbuff = points.buffer(150)
    assert ptbuff.geomtype == "Polygon"


def test_line_buffer(lines):
    linebuff = lines.buffer(150)
    assert linebuff.geomtype == "Polygon"


def test_poly_buffer(polygons):
    polybuff = polygons.buffer(150)
    assert polybuff.geomtype == "Polygon"


#TODO multi part features

def test_line_simplify(lines):
    d = lines.simplify(150)
    assert d.geomtype == "LineString"

def test_line_centroid(polygons):
    d = polygons.centroid()
    assert d.geomtype == "Point"
