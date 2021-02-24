from config import api
from .policy_category import PolicyCategory, PolicyCategoryListSearch

#urls apis basicas
#api.add_resource(PolicyCategory, '/api/policy_categories/create',endpoint="api-policy_categories-post", methods=["POST"])
api.add_resource(PolicyCategory, '/api/policy_categories/search/<int:id>',endpoint="api-policy_categories-get-by-id", methods=["GET"])
#api.add_resource(PolicyCategory, '/api/policy_categories/update/<int:id>',endpoint="api-policy_categories-put", methods=["PUT"])
#api.add_resource(PolicyCategory, '/api/policy_categories/delete/<int:id>',endpoint="api-policy_categories-delete", methods=["DELETE"])
api.add_resource(PolicyCategoryListSearch, '/api/policy_categories/get',endpoint="api-policy_categories-get-all", methods=["GET"])