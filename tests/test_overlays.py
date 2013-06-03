# test overlays


def test_intersection(polygons, lines):
    linebuff = lines.buffer(150)
    intr = linebuff.intersection(polygons)
    assert intr.geomtype == "Polygon"


def test_identity(polygons, lines):
    linebuff = lines.buffer(150)
    idline = linebuff.identity(polygons)
    idpoly = polygons.identity(linebuff)
    assert idline.geomtype == "Polygon"
    assert idpoly.geomtype == "Polygon"


def test_union(polygons, lines):
    linebuff = lines.buffer(150)
    unioned = linebuff.union(polygons)
    assert unioned.geomtype == "Polygon"

# TODO test with multipolygon for input & output

# TODO test for lines and points as a and b
