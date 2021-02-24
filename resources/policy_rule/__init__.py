from config import api
from .policy_rule import PolicyRuleListSearch, PolicyRule

#urls apis basicas
#api.add_resource(PolicyRule, '/api/policy_rules/create',endpoint="api-policy_rules-post", methods=["POST"])
api.add_resource(PolicyRule, '/api/policy_rules/search/<int:id>',endpoint="api-policy_rules-get-by-id", methods=["GET"])
#api.add_resource(PolicyRule, '/api/policy_rules/update/<int:id>',endpoint="api-policy_rules-put", methods=["PUT"])
#api.add_resource(PolicyRule, '/api/policy_rules/delete/<int:id>',endpoint="api-policy_rules-delete", methods=["DELETE"])
api.add_resource(PolicyRuleListSearch, '/api/policy_rules/get',endpoint="api-policy_rules-get-all", methods=["GET"])