from config import api
from .age_code import AgeCodeListSearch, AgeCode

#urls apis basicas
api.add_resource(AgeCode, '/api/age-code/create',endpoint="api-age-code-post", methods=["POST"])
api.add_resource(AgeCode, '/api/age-code/search/<int:id>',endpoint="api-age-code-get-by-id", methods=["GET"])
api.add_resource(AgeCode, '/api/age-code/update/<int:id>',endpoint="api-age-code-put", methods=["PUT"])
api.add_resource(AgeCode, '/api/age-code/delete/<int:id>',endpoint="api-age-code-delete", methods=["DELETE"])
api.add_resource(AgeCodeListSearch, '/api/age-code/get',endpoint="api-age-code-get-all", methods=["GET"])