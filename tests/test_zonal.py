# test zonal stats


def test_zonal(polygons, raster):
    stats = polygons.zonal_stats(raster)
    assert sorted(stats[0].keys()) == sorted(
        ['std', 'count', 'min', 'max', 'sum', 'fid', 'mean'])
    assert len(stats) == polygons.feature_count
