from config import api
from .policy_guarantee import PolicyGuaranteeListSearch, PolicyGuarantee, PolicyGuaranteeDelete

#urls apis basicas
api.add_resource(PolicyGuaranteeListSearch, '/api/policy_guarantees/create',endpoint="api-policy_guarantees-post", methods=["POST"])
api.add_resource(PolicyGuarantee, '/api/policy_guarantees/search/<int:id>',endpoint="api-policy_guarantees-get-by-id", methods=["GET"])
api.add_resource(PolicyGuarantee, '/api/policy_guarantees/update/<int:id>',endpoint="api-policy_guarantees-put", methods=["PUT"])
api.add_resource(PolicyGuaranteeDelete, '/api/policy_guarantees/delete/<int:id>',endpoint="api-policy_guarantees-delete", methods=["PUT"])
api.add_resource(PolicyGuaranteeListSearch, '/api/policy_guarantees/get',endpoint="api-policy_guarantees-get-all", methods=["GET"])