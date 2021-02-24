from config import api
from .policy_cancellation_penalty import PolicyCancellationPenaltyListSearch

#urls apis basicas
api.add_resource(PolicyCancellationPenaltyListSearch, '/api/policy-cancellation-penalty/get',endpoint="api-policy-cancellation-penalty-get-all", methods=["GET"])