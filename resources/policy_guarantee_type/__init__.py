from config import api
from .policy_guarantee_type import PolicyGuaranteeTypeListSearch, PolicyGuaranteeType

#urls apis basicas
#api.add_resource(PolicyGuaranteeType, '/api/policy_guarantee_types/create',endpoint="api-policy_guarantee_types-post", methods=["POST"])
api.add_resource(PolicyGuaranteeType, '/api/policy_guarantee_types/search/<int:id>',endpoint="api-policy_guarantee_types-get-by-id", methods=["GET"])
#api.add_resource(PolicyGuaranteeType, '/api/policy_guarantee_types/update/<int:id>',endpoint="api-policy_guarantee_types-put", methods=["PUT"])
#api.add_resource(PolicyGuaranteeType, '/api/policy_guarantee_types/delete/<int:id>',endpoint="api-policy_guarantee_types-delete", methods=["DELETE"])
api.add_resource(PolicyGuaranteeTypeListSearch, '/api/policy_guarantee_types/get',endpoint="api-policy_guarantee_types-get-all", methods=["GET"])