from config import api
from .property_filters import Propertyfilters, PropertyfiltersListSearch, PublicPropertyfiltersListSearch

#urls apis basicas
api.add_resource(Propertyfilters, '/api/property-filters/create',endpoint="api-property-filters-post", methods=["POST"])
api.add_resource(Propertyfilters, '/api/property-filters/search/<int:id>',endpoint="api-property-filters-get-by-id", methods=["GET"])
api.add_resource(Propertyfilters, '/api/property-filters/update/<int:id>',endpoint="api-property-filters-put", methods=["PUT"])
api.add_resource(Propertyfilters, '/api/property-filters/delete/<int:id>',endpoint="api-property-filters-delete", methods=["DELETE"])
api.add_resource(PropertyfiltersListSearch, '/api/property-filters/get',endpoint="api-property-filters-get-all", methods=["GET"])

#Apis publicas
api.add_resource(PublicPropertyfiltersListSearch, '/api/public/property-filters/get',endpoint="api-public-property-filters-get-all", methods=["POST"])