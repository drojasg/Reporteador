from config import api
from .promotions import Promotions, PromotionsListSearch

#urls apis basicas
api.add_resource(PromotionsListSearch, '/api/promotions/get',endpoint="api-promotions-get-all", methods=["GET"])
api.add_resource(Promotions, '/api/promotions/create',endpoint="api-promotions-post", methods=["POST"])
api.add_resource(Promotions, '/api/promotions/search/<int:id>',endpoint="api-promotions-get-by-id", methods=["GET"])
api.add_resource(Promotions, '/api/promotions/delete/<int:id>/<int:status>',endpoint="api-promotions-update-status", methods=["PUT"])