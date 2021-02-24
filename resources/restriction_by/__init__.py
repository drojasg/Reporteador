from config import api
from .restriction_by import RestrictionBy, RestrictionBySearch

#urls apis basicas
api.add_resource(RestrictionBy, '/api/restriction-by/create',endpoint="api-restriction-by-post", methods=["POST"])
api.add_resource(RestrictionBy, '/api/restriction-by/search/<int:id>',endpoint="api-restriction-by-get-by-id", methods=["GET"])
api.add_resource(RestrictionBy, '/api/restriction-by/update/<int:id>',endpoint="api-restriction-by-put", methods=["PUT"])
api.add_resource(RestrictionBy, '/api/restriction-by/delete/<int:id>',endpoint="api-restriction-by-delete", methods=["DELETE"])
api.add_resource(RestrictionBySearch, '/api/restriction-by/get',endpoint="api-restriction-by-get-all", methods=["GET"])