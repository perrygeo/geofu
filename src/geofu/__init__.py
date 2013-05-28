# -*- coding: utf-8 -*-
"""
geofu
"""
from geofu._layer import Layer


def load(path):
    import os
    #TODO more robust test for vector layer-ness
    if not os.path.exists(path):
        raise IOError("no such file or directory: %r" % path)
    c = Layer(path)
    return c
