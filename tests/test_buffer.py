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
