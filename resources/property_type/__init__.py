from config import api
from .property_type import PropertyTypeListSearch, PropertyType

#urls apis basicas
api.add_resource(PropertyType, '/api/property-type/create',endpoint="api-property-type-post", methods=["POST"])
api.add_resource(PropertyType, '/api/property-type/search/<int:id>',endpoint="api-property-type-get-by-id", methods=["GET"])
api.add_resource(PropertyType, '/api/property-type/update/<int:id>',endpoint="api-property-type-put", methods=["PUT"])
api.add_resource(PropertyType, '/api/property-type/delete/<int:id>',endpoint="api-property-type-delete", methods=["DELETE"])
api.add_resource(PropertyTypeListSearch, '/api/property-type/get',endpoint="api-property-type-get-all", methods=["GET"])