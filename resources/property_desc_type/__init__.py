from config import api
from .property_desc_type import DescType, DescTypeList

#urls apis basicas
api.add_resource(DescType, '/api/property-desc-type/create',endpoint="api-property-desc-type-post", methods=["POST"])
api.add_resource(DescType, '/api/property-desc-type/search/<int:id>',endpoint="api-property-desc-type-get-by-id", methods=["GET"])
api.add_resource(DescType, '/api/property-desc-type/update/<int:id>',endpoint="api-property-desc-type-put", methods=["PUT"])
api.add_resource(DescType, '/api/property-desc-type/delete/<int:id>',endpoint="api-property-desc-type-delete", methods=["DELETE"])
api.add_resource(DescTypeList, '/api/property-desc-type/get',endpoint="api-property-desc-type-get-all", methods=["GET"])