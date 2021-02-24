from config import api
from .policy_tax_base import PolicyTaxBaseListSearch, PolicyTaxBase

#urls apis basicas
#api.add_resource(PolicyTaxBase, '/api/policy_tax_bases/create',endpoint="api-policy_tax_bases-post", methods=["POST"])
api.add_resource(PolicyTaxBase, '/api/policy_tax_bases/search/<int:id>',endpoint="api-policy_tax_bases-get-by-id", methods=["GET"])
#api.add_resource(PolicyTaxBase, '/api/policy_tax_bases/update/<int:id>',endpoint="api-policy_tax_bases-put", methods=["PUT"])
#api.add_resource(PolicyTaxBase, '/api/policy_tax_bases/delete/<int:id>',endpoint="api-policy_tax_bases-delete", methods=["DELETE"])
api.add_resource(PolicyTaxBaseListSearch, '/api/policy_tax_bases/get',endpoint="api-policy_tax_bases-get-all", methods=["GET"])