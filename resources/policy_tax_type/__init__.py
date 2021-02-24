from config import api
from .policy_tax_type import PolicyTaxTypeListSearch, PolicyTaxType

#urls apis basicas
#api.add_resource(PolicyTaxType, '/api/policy_tax_types/create',endpoint="api-policy_tax_types-post", methods=["POST"])
api.add_resource(PolicyTaxType, '/api/policy_tax_types/search/<int:id>',endpoint="api-policy_tax_types-get-by-id", methods=["GET"])
#api.add_resource(PolicyTaxType, '/api/policy_tax_types/update/<int:id>',endpoint="api-policy_tax_types-put", methods=["PUT"])
#api.add_resource(PolicyTaxType, '/api/policy_tax_types/delete/<int:id>',endpoint="api-policy_tax_types-delete", methods=["DELETE"])
api.add_resource(PolicyTaxTypeListSearch, '/api/policy_tax_types/get',endpoint="api-policy_tax_types-get-all", methods=["GET"])