from config import api
from .amenity_type import AmenityTypeListSearch, AmenityType,AmenityTypeUpdateStatus

#urls apis basicas
api.add_resource(AmenityType, '/api/amenity-type/create',endpoint="api-amenity-type-post", methods=["POST"])
api.add_resource(AmenityType, '/api/amenity-type/search/<int:id>',endpoint="api-amenity-type-get-by-id", methods=["GET"])
api.add_resource(AmenityType, '/api/amenity-type/update/<int:id>',endpoint="api-amenity-type-put", methods=["PUT"])
api.add_resource(AmenityTypeUpdateStatus, '/api/amenity-type/delete/<int:id>',endpoint="api-amenity-type-delete", methods=["PUT"])
api.add_resource(AmenityTypeListSearch, '/api/amenity-type/get',endpoint="api-amenity-type-get-all", methods=["GET"])