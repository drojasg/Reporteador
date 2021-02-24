from config import api
from .rateplan_prices import RatePlanPricesListSearch, RatePlanPrices

#urls apis basicas
api.add_resource(RatePlanPrices, '/api/rates-prices/create',endpoint="api-rates-prices-post", methods=["POST"])
api.add_resource(RatePlanPrices, '/api/rates-prices/search/<int:id>',endpoint="api-rates-prices-get-by-id", methods=["GET"])
api.add_resource(RatePlanPrices, '/api/rates-prices/update/<int:id>',endpoint="api-rates-prices-put", methods=["PUT"])
api.add_resource(RatePlanPrices, '/api/rates-prices/delete/<int:id>',endpoint="api-rates-prices-delete", methods=["DELETE"])
api.add_resource(RatePlanPricesListSearch, '/api/rates-prices/get',endpoint="api-rates-prices-get-all", methods=["GET"])