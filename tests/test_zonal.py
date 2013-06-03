# test zonal stats


def test_zonal(polygons, raster):
    stats = polygons.zonal_stats(raster)
    assert sorted(stats[0].keys()) == sorted(
        ['std', 'count', 'min', 'max', 'sum', 'fid', 'mean'])
    assert len(stats) == polygons.feature_count

def test_zonal_global_extent(polygons, raster):
    stats = polygons.zonal_stats(raster, global_src_extent=True)
    assert sorted(stats[0].keys()) == sorted(
        ['std', 'count', 'min', 'max', 'sum', 'fid', 'mean'])
    assert len(stats) == polygons.feature_count

def test_zonal_nodata(polygons, raster):
    stats = polygons.zonal_stats(raster, nodata_value=0)
    assert sorted(stats[0].keys()) == sorted(
        ['std', 'count', 'min', 'max', 'sum', 'fid', 'mean'])
    assert len(stats) == polygons.feature_count
