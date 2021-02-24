from config import api
from .policy_cancellation_detail import PolicyCancellationDetailListSearch, PolicyCancellationDetail, GetIdPolicyCancellationDetail, PolicyCancellationDetailDelete

#urls apis basicas
api.add_resource(PolicyCancellationDetail, '/api/policy-cancellation/create',endpoint="api-policy-cancellation-post", methods=["POST"])
api.add_resource(PolicyCancellationDetail, '/api/policy-cancellation/search/<int:id>',endpoint="api-policy-cancellation-get-by-id", methods=["GET"])
api.add_resource(PolicyCancellationDetail, '/api/policy-cancellation/update/<int:id>',endpoint="api-policy-cancellation-put", methods=["PUT"])
api.add_resource(PolicyCancellationDetailDelete, '/api/policy-cancellation/delete/<int:id>/<int:status>',endpoint="api-policy-cancellation-delete", methods=["PUT"])
api.add_resource(PolicyCancellationDetailListSearch, '/api/policy-cancellation/get',endpoint="api-policy_cancellation-get-all", methods=["GET"])
api.add_resource(GetIdPolicyCancellationDetail, '/api/policy-cancellation/get_by_policy/<int:id_policy>', endpoint="api-policy-cancellation-get-by-id-policy", methods=["GET"])