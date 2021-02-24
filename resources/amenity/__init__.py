from config import api
from .amenity import AmenityListSearch, Amenity, AmenityUpdateStatus

#urls apis basicas
api.add_resource(Amenity, '/api/amenity/create',endpoint="api-amenity-post", methods=["POST"])
api.add_resource(Amenity, '/api/amenity/search/<int:id>',endpoint="api-amenity-get-by-id", methods=["GET"])
api.add_resource(Amenity, '/api/amenity/update/<int:id>',endpoint="api-amenity-put", methods=["PUT"])
api.add_resource(Amenity, '/api/amenity/delete/<int:id>',endpoint="api-amenity-delete", methods=["DELETE"])
api.add_resource(AmenityListSearch, '/api/amenity/get',endpoint="api-amenity-get-all", methods=["GET"])
api.add_resource(AmenityUpdateStatus, '/api/amenity/update-status/<int:id>',endpoint="api-amenity-update-status", methods=["PUT"])