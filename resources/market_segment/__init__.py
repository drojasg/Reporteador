from config import api
from .market_segment import MarketSegment, MarketSegmentSearch

#urls apis basicas
api.add_resource(MarketSegment, '/api/market/create',endpoint="api-market-post", methods=["POST"])
api.add_resource(MarketSegment, '/api/market/search/<int:id>',endpoint="api-market-get-by-id", methods=["GET"])
api.add_resource(MarketSegment, '/api/market/update/<int:id>',endpoint="api-market-put", methods=["PUT"])
api.add_resource(MarketSegment, '/api/market/delete/<int:id>',endpoint="api-market-delete", methods=["DELETE"])
api.add_resource(MarketSegmentSearch, '/api/market/get',endpoint="api-market-get-all", methods=["GET"])