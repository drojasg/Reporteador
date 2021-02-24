from config import api
from .policy_penalty_cancel_fee import PolicyPenaltyCancelFeeListSearch, PolicyPenaltyCancelFee, PolicyPenaltyCancelFeeDefault, PolicyPenaltyCancelFeeList, PolicyPenaltyCancelFeeByCancelPenalty

#urls apis basicas
api.add_resource(PolicyPenaltyCancelFee, '/api/policy_penalty_cancel_fees/create',endpoint="api-policy_penalty_cancel_fees-post", methods=["POST"])
api.add_resource(PolicyPenaltyCancelFee, '/api/policy_penalty_cancel_fees/search/<int:id>',endpoint="api-policy_penalty_cancel_fees-get-by-id", methods=["GET"])
api.add_resource(PolicyPenaltyCancelFee, '/api/policy_penalty_cancel_fees/update/<int:id>',endpoint="api-policy_penalty_cancel_fees-put", methods=["PUT"])
#api.add_resource(PolicyPenaltyCancelFee, '/api/policy_penalty_cancel_fees/delete/<int:id>',endpoint="api-policy_penalty_cancel_fees-delete", methods=["DELETE"])
api.add_resource(PolicyPenaltyCancelFeeListSearch, '/api/policy_penalty_cancel_fees/get',endpoint="api-policy_penalty_cancel_fees-get-all", methods=["GET"])
#api.add_resource(PolicyPenaltyCancelFeeDefault, '/api/policy_penalty_cancel_fees/get_by_cancel-penalty/<int:id_policy_cancel_penalty>', endpoint="api-policy_cancel_fees-get-by-id-policy", methods=["GET"])
#api.add_resource(PolicyPenaltyCancelFeeList, '/api/policy_penalty_cancel_fees/create_by_cancel_penalty',endpoint="api-policy_cancel_penalties-post-by-cancel-penalty", methods=["POST"])
api.add_resource(PolicyPenaltyCancelFeeByCancelPenalty, '/api/policy_penalty_cancel_fees/update_by_cancel_penalty/<int:iddef_policy_cancel_penalty>',endpoint="api-policy_cancel_fees_by_cancel_penalty-put", methods=["PUT"])