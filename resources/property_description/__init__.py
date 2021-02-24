from config import api
from .property_description import PropertyDescription, PropertyDescriptionList, PropertyDescriptionListSearch

#urls apis basicas
#api.add_resource(PropertyDescription, '/api/property-description/create',endpoint="api-property-description-post", methods=["POST"])
#api.add_resource(PropertyDescription, '/api/property-description/search/<int:id>',endpoint="api-property-description-get-by-id", methods=["GET"])
api.add_resource(PropertyDescription, '/api/property-description/update/<int:id>',endpoint="api-property-description-put", methods=["PUT"])
api.add_resource(PropertyDescription, '/api/property-description/delete/<int:id>',endpoint="api-property-description-delete", methods=["DELETE"])
#api.add_resource(BrandListSearch, '/api/property-description/get',endpoint="api-property-description-get-all", methods=["GET"])

#Funciones extras
api.add_resource(PropertyDescriptionList, '/api/property-description/create/all',endpoint="api-property-description-post-list", methods=["POST"])
api.add_resource(PropertyDescriptionList, '/api/property-description/search/<string:hotelcode>/<int:type>',endpoint="api-property-description-get-by-params", methods=["GET"])
api.add_resource(PropertyDescriptionList, '/api/property-description/update/all',endpoint="api-property-description-put-list", methods=["PUT"])
#api.add_resource(PropertyDescription, '/api/property-description/delete/<int:id>',endpoint="api-property-description-delete-list", methods=["DELETE"])