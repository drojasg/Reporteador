from config import api
from .area_unit import AreaUnitListSearch, AreaUnit

#urls apis basicas
api.add_resource(AreaUnit, '/api/area-unit/create',endpoint="api-area-unit-post", methods=["POST"])
api.add_resource(AreaUnit, '/api/area-unit/search/<int:id>',endpoint="api-area-unit-get-by-id", methods=["GET"])
api.add_resource(AreaUnit, '/api/area-unit/update/<int:id>',endpoint="api-area-unit-put", methods=["PUT"])
api.add_resource(AreaUnit, '/api/area-unit/delete/<int:id>',endpoint="api-area-unit-delete", methods=["DELETE"])
api.add_resource(AreaUnitListSearch, '/api/area-unit/get',endpoint="api-area-unit-get-all", methods=["GET"])