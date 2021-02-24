from config import api
from .policy import Policy, PolicyListSearch, PolicyListCategorySearch, PolicyDefault, PolicyPropertyCategorySearch,\
PolicyDelete, PolicyDefaultListSearch, PolicyStatus, PublicPolicies

#urls apis basicas
api.add_resource(PolicyListSearch, '/api/policies/create',endpoint="api-policies-post", methods=["POST"])
api.add_resource(PolicyDefault, '/api/policies/search/<int:id>',endpoint="api-policies-get-default-by-id", methods=["GET"])
#api.add_resource(Policy, '/api/policies/search/<int:id>/<int:category>',endpoint="api-policies-get-by-id", methods=["GET"])
api.add_resource(Policy, '/api/policies/update/<int:id>',endpoint="api-policies-put", methods=["PUT"])
api.add_resource(PolicyDelete, '/api/policies/delete/<int:id>',endpoint="api-policies-delete", methods=["PUT"])
api.add_resource(PolicyStatus, '/api/policies/change_status/<int:id>/<int:estado>',endpoint="api-policies-change-status", methods=["PUT"])
api.add_resource(PolicyListSearch, '/api/policies/get',endpoint="api-policies-get-all", methods=["GET"])
api.add_resource(PolicyListCategorySearch, '/api/policies/get/<int:category>',endpoint="api-policies-get-all-category", methods=["GET"])
#api.add_resource(PolicyListPropertySearch, '/api/policies/get_property/<int:property>', endpoint="api-policies-get_property-all", methods=["GET"])
#api.add_resource(PolicyPropertyCategorySearch, '/api/policies/get_property/<int:property>/<int:category>', endpoint="api-policies-get_property-all-category", methods=["GET"])
api.add_resource(PolicyPropertyCategorySearch, '/api/policies/set_default/<int:id>/<int:category>', endpoint="api-policies-set_default-all-category", methods=["PUT"])
api.add_resource(PolicyDefault, '/api/policies/single_create',endpoint="api-policies-post-single", methods=["POST"])
api.add_resource(PolicyDefault, '/api/policies/single_update/<int:id>',endpoint="api-policies-single-put", methods=["PUT"])
api.add_resource(PolicyDefaultListSearch, '/api/policies/single_get',endpoint="api-policies-get-all-single", methods=["GET"])

#Apis publicas
api.add_resource(PublicPolicies, '/api/public/policies_ratesplans/get',endpoint="api-public-policies_ratesplans-post", methods=["POST"])
