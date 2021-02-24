from config import api
from .policy_guarantee_deposit import PolicyGuaranteeDepositListSearch, PolicyGuaranteeDeposit, PolicyGuaranteeDepositByGuarantee, PolicyGuaranteeDepositDelete

#urls apis basicas
api.add_resource(PolicyGuaranteeDepositListSearch, '/api/policy_guarantee_deposits/create',endpoint="api-policy_guarantee_deposits-post", methods=["POST"])
api.add_resource(PolicyGuaranteeDeposit, '/api/policy_guarantee_deposits/search/<int:id>',endpoint="api-policy_guarantee_deposits-get-by-id", methods=["GET"])
api.add_resource(PolicyGuaranteeDeposit, '/api/policy_guarantee_deposits/update/<int:id>',endpoint="api-policy_guarantee_deposits-put", methods=["PUT"])
api.add_resource(PolicyGuaranteeDepositDelete, '/api/policy_guarantee_deposits/delete/<int:id>',endpoint="api-policy_guarantee_deposits-delete", methods=["PUT"])
api.add_resource(PolicyGuaranteeDepositListSearch, '/api/policy_guarantee_deposits/get',endpoint="api-policy_guarantee_deposits-get-all", methods=["GET"])
api.add_resource(PolicyGuaranteeDepositByGuarantee, '/api/policy_guarantee_deposits/update_by_guarantee/<int:iddef_policy_guarantee>',endpoint="api-policy_guarantee_deposits_by_guarantee-put", methods=["PUT"])