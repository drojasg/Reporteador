from config import api
from .rateplan import RatePlanListSearch, RatePlan, RatePlanDefault, RatePlanPublic

#urls apis basicas
api.add_resource(RatePlan, '/api/rate-plan/create',endpoint="api-rate-plan-post", methods=["POST"])
api.add_resource(RatePlan, '/api/rate-plan/search/<int:id>',endpoint="api-rate-plan-get-by-id", methods=["GET"])
api.add_resource(RatePlan, '/api/rate-plan/update/<int:id>',endpoint="api-rate-plan-put", methods=["PUT"])
#api.add_resource(RatePlan, '/api/rate-plan/delete/<int:id>',endpoint="api-rate-plan-delete", methods=["DELETE"])
api.add_resource(RatePlanListSearch, '/api/rate-plan/get',endpoint="api-rate-plan-get-all", methods=["GET"])
api.add_resource(RatePlanDefault, '/api/rate-plan/update-estado/<int:id>',endpoint="api-rate-plan-put-estado", methods=["PUT"])

#Apis publicas
api.add_resource(RatePlanPublic, '/api/public/rate-plan/search/<int:id>/<string:lang_code>',endpoint="api-public-rate-plan-get-id", methods=["GET"])
#api.add_resource(RatePlanPublic, '/api/public/room-rate-plan/get',endpoint="api-public-room-rate-plan-get", methods=["POST"])