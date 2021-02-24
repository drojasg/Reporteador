from config import api
from .price_type import PriceTypeListSearch, PriceType

#urls apis basicas
api.add_resource(PriceType, '/api/price-type/create',endpoint="api-price-type-post", methods=["POST"])
api.add_resource(PriceType, '/api/price-type/search/<int:id>',endpoint="api-price-type-get-by-id", methods=["GET"])
api.add_resource(PriceType, '/api/price-type/update/<int:id>',endpoint="api-price-type-put", methods=["PUT"])
api.add_resource(PriceType, '/api/price-type/delete/<int:id>',endpoint="api-price-type-delete", methods=["DELETE"])
api.add_resource(PriceTypeListSearch, '/api/price-type/get',endpoint="api-price-type-get-all", methods=["GET"])