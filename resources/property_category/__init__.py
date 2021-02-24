from config import api
from .property_category import PropertyCategoryListSearch, PropertyCategory

#urls apis basicas
api.add_resource(PropertyCategory, '/api/property-category/create',endpoint="api-property-category-post", methods=["POST"])
api.add_resource(PropertyCategory, '/api/property-category/search/<int:id>',endpoint="api-property-category-get-by-id", methods=["GET"])
api.add_resource(PropertyCategory, '/api/property-category/update/<int:id>',endpoint="api-property-category-put", methods=["PUT"])
api.add_resource(PropertyCategory, '/api/property-category/delete/<int:id>',endpoint="api-property-category-delete", methods=["DELETE"])
api.add_resource(PropertyCategoryListSearch, '/api/property-category/get',endpoint="api-property-category-get-all", methods=["GET"])