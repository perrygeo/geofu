from fiona import crs


def guess_crs(thing):
    try:
        #is it a crs object itself?
        if thing.keys() and \
           set(thing.keys()).issubset(set(crs.all_proj_keys)):
            return thing
    except AttributeError:
        pass

    try:
        # is it a collection or something else with a crs attr?
        return thing.crs
    except AttributeError:
        pass

    try:
        # if it's an int, use an epsg code
        epsg = int(thing)
        return crs.from_epsg(epsg)
    except ValueError:
        pass

    # finally try a string parser
    return crs.from_string(thing)


def bbox_to_pixel_offsets(gt, bbox):
    originX = gt[0]
    originY = gt[3]
    pixel_width = gt[1]
    pixel_height = gt[5]
    x1 = int((bbox[0] - originX) / pixel_width)
    x2 = int((bbox[1] - originX) / pixel_width) + 1

    y1 = int((bbox[3] - originY) / pixel_height)
    y2 = int((bbox[2] - originY) / pixel_height) + 1

    xsize = x2 - x1
    ysize = y2 - y1
    return (x1, y1, xsize, ysize)
