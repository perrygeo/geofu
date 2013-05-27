from shapely.wkt import loads
from shapely.ops import unary_union

mls = loads(open("bad_mls.wkt", 'r').read())

import ipdb; ipdb.set_trace()

mm = unary_union(mls)
