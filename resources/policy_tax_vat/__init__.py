from config import api
from .policy_tax_vat import PolicyTaxVatListSearch, PolicyTaxVat

#urls apis basicas
#api.add_resource(PolicyTaxVat, '/api/policy_tax_vats/create',endpoint="api-policy_tax_vats-post", methods=["POST"])
api.add_resource(PolicyTaxVat, '/api/policy_tax_vats/search/<int:id>',endpoint="api-policy_tax_vats-get-by-id", methods=["GET"])
#api.add_resource(PolicyTaxVat, '/api/policy_tax_vats/update/<int:id>',endpoint="api-policy_tax_vats-put", methods=["PUT"])
#api.add_resource(PolicyTaxVat, '/api/policy_tax_vats/delete/<int:id>',endpoint="api-policy_tax_vats-delete", methods=["DELETE"])
api.add_resource(PolicyTaxVatListSearch, '/api/policy_tax_vats/get',endpoint="api-policy_tax_vats-get-all", methods=["GET"])