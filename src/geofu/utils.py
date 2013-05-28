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
