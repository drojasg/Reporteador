from config import api
from .amenity_group import AmenityGroupListSearch, AmenityGroup, AmenityGroupListSearchType,AmenityGroupUpdateStatus

#urls apis basicas
api.add_resource(AmenityGroup, '/api/amenity-group/create',endpoint="api-amenity-group-post", methods=["POST"])
api.add_resource(AmenityGroup, '/api/amenity-group/search/<int:id>',endpoint="api-amenity-group-get-by-id", methods=["GET"])
api.add_resource(AmenityGroup, '/api/amenity-group/update/<int:id>',endpoint="api-amenity-group-put", methods=["PUT"])
api.add_resource(AmenityGroupUpdateStatus, '/api/amenity-group/delete/<int:id>',endpoint="api-amenity-group-delete", methods=["PUT"])
api.add_resource(AmenityGroupListSearch, '/api/amenity-group/get',endpoint="api-amenity-group-get-all", methods=["GET"])
api.add_resource(AmenityGroupListSearchType, '/api/amenity-group/search-type/<int:type>',endpoint="api-amenity-group-get-search-type", methods=["GET"])