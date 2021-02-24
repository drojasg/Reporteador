from config import api
from .zone import ZoneListSearch, Zone

#urls apis basicas
api.add_resource(Zone, '/api/zones/create',endpoint="api-zones-post", methods=["POST"])
api.add_resource(Zone, '/api/zones/search/<int:id>',endpoint="api-zones-get-by-id", methods=["GET"])
api.add_resource(Zone, '/api/zones/update/<int:id>',endpoint="api-zones-put", methods=["PUT"])
api.add_resource(Zone, '/api/zones/delete/<int:id>',endpoint="api-zones-delete", methods=["DELETE"])
api.add_resource(ZoneListSearch, '/api/zones/get',endpoint="api-zones-get-all", methods=["GET"])