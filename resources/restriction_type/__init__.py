from config import api
from .restriction_type import RestrictionType, RestrictionsTypeSearch

#urls apis basicas
api.add_resource(RestrictionType, '/api/restriction-type/create',endpoint="api-restriction-type-post", methods=["POST"])
api.add_resource(RestrictionType, '/api/restriction-type/search/<int:id>',endpoint="api-restriction-type-get-by-id", methods=["GET"])
api.add_resource(RestrictionType, '/api/restriction-type/update/<int:id>',endpoint="api-restriction-type-put", methods=["PUT"])
api.add_resource(RestrictionType, '/api/restriction-type/delete/<int:id>',endpoint="api-restriction-type-delete", methods=["DELETE"])
api.add_resource(RestrictionsTypeSearch, '/api/restriction-type/get',endpoint="api-restriction-type-get-all", methods=["GET"])