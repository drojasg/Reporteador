from config import api
from .policy_cancellation_option import PolicyCancellationOptionListSearch

#urls apis basicas
api.add_resource(PolicyCancellationOptionListSearch, '/api/policy-cancellation-option/get',endpoint="api-policy-cancellation-option-get-all", methods=["GET"])