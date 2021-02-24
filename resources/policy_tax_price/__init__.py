from config import api
from .policy_tax_price import PolicyTaxPriceListSearch, PolicyTaxPrice

#urls apis basicas
#api.add_resource(PolicyTaxPrice, '/api/policy_tax_prices/create',endpoint="api-policy_tax_prices-post", methods=["POST"])
api.add_resource(PolicyTaxPrice, '/api/policy_tax_prices/search/<int:id>',endpoint="api-policy_tax_prices-get-by-id", methods=["GET"])
#api.add_resource(PolicyTaxPrice, '/api/policy_tax_prices/update/<int:id>',endpoint="api-policy_tax_prices-put", methods=["PUT"])
#api.add_resource(PolicyTaxPrice, '/api/policy_tax_prices/delete/<int:id>',endpoint="api-policy_tax_prices-delete", methods=["DELETE"])
api.add_resource(PolicyTaxPriceListSearch, '/api/policy_tax_prices/get',endpoint="api-policy_tax_prices-get-all", methods=["GET"])