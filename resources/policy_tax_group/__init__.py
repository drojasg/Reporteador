from config import api
from .policy_tax_group import PolicyTaxGroupListSearch, PolicyTaxGroup, PolicyTaxGroupDelete

#urls apis basicas
api.add_resource(PolicyTaxGroupListSearch, '/api/policy_tax_groups/create',endpoint="api-policy_tax_groups-post", methods=["POST"])
api.add_resource(PolicyTaxGroup, '/api/policy_tax_groups/search/<int:id>',endpoint="api-policy_tax_groups-get-by-id", methods=["GET"])
api.add_resource(PolicyTaxGroup, '/api/policy_tax_groups/update/<int:id>',endpoint="api-policy_tax_groups-put", methods=["PUT"])
api.add_resource(PolicyTaxGroupDelete, '/api/policy_tax_groups/delete/<int:id>',endpoint="api-policy_tax_groups-delete", methods=["PUT"])
api.add_resource(PolicyTaxGroupListSearch, '/api/policy_tax_groups/get',endpoint="api-policy_tax_groups-get-all", methods=["GET"])