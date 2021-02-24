from config import api
from .policy_cancel_penalty import PolicyCancelPenaltyListSearch, PolicyCancelPenalty, PolicyCancelPenaltyDefault, PolicyCancelPenaltyDelete

#urls apis basicas
api.add_resource(PolicyCancelPenalty, '/api/policy_cancel_penalties/create',endpoint="api-policy_cancel_penalties-post", methods=["POST"])
api.add_resource(PolicyCancelPenalty, '/api/policy_cancel_penalties/search/<int:id>',endpoint="api-policy_cancel_penalties-get-by-id", methods=["GET"])
api.add_resource(PolicyCancelPenalty, '/api/policy_cancel_penalties/update/<int:id>',endpoint="api-policy_cancel_penalties-put", methods=["PUT"])
api.add_resource(PolicyCancelPenaltyDelete, '/api/policy_cancel_penalties/delete/<int:id>',endpoint="api-policy_cancel_penalties-delete", methods=["PUT"])
api.add_resource(PolicyCancelPenaltyListSearch, '/api/policy_cancel_penalties/get',endpoint="api-policy_cancel_penalties-get-all", methods=["GET"])
api.add_resource(PolicyCancelPenaltyDefault, '/api/policy_cancel_penalties/get_by_policy/<int:id_policy>', endpoint="api-policy_cancel_penalties-get-by-id-policy", methods=["GET"])
#api.add_resource(PolicyCancelPenaltyListSearch, '/api/policy_cancel_penalties/create_by_policy',endpoint="api-policy_cancel_penalties-post-by-policy", methods=["POST"])