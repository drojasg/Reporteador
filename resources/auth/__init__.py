from config import api
from .auth_item import AuthItem, AuthItemSearch,AuthItemSearchDropDown
from .auth_assignment import  AuthAssignment, AuthAssignmentSearch
from .auth_item_child import AuthItemChild, AuthItemChildSearch
from .auth_profile_view import AuthProfileView, AuthProfileViewSearch, AuthProfileViewRole

api.add_resource(AuthItem, '/api/auth-item/search/<string:name>',endpoint="api-auth-item-get", methods=["GET"])
api.add_resource(AuthItem, '/api/auth-item/create',endpoint="api-auth-item-post", methods=["POST"])
api.add_resource(AuthItem, '/api/auth-item/update/<string:name>',endpoint="api-auth-item-put", methods=["PUT"])
api.add_resource(AuthItemSearch, '/api/auth-item/get',endpoint="api-auth-item-get-all", methods=["GET"])
api.add_resource(AuthItemSearchDropDown, '/api/auth-item/get-dropdown', endpoint="api-auth-item-get-all-dropdown", methods=["GET"])

api.add_resource(AuthAssignment, '/api/auth-assignment/search/<string:item_name>/<int:credentials_id>',endpoint="api-auth-assignment-get", methods=["GET"])
api.add_resource(AuthAssignment, '/api/auth-assignment/create',endpoint="api-auth-assignment-post", methods=["POST"])
api.add_resource(AuthAssignment, '/api/auth-assignment/update-status/<string:item_name>/<int:credentials_id>',endpoint="api-auth-assignment-update-status", methods=["PUT"])
api.add_resource(AuthAssignmentSearch, '/api/auth-assignment/get/<int:credentials_id>',endpoint="api-auth-assignment-get-all", methods=["GET"])

api.add_resource(AuthItemChild, '/api/auth-child/search/<string:parent>/<string:child>',endpoint="api-auth-child-get", methods=["GET"])
api.add_resource(AuthItemChild, '/api/auth-child/create',endpoint="api-auth-child-post", methods=["POST"])
api.add_resource(AuthItemChild, '/api/auth-child/update/<string:parent>/<string:child>',endpoint="api-auth-child-update", methods=["PUT"])
api.add_resource(AuthItemChildSearch, '/api/auth-child/get/<string:parent>',endpoint="api-auth-child-get-all", methods=["GET"])

api.add_resource(AuthProfileView, '/api/auth-profile-view/search/<int:id>',endpoint="api-auth-profile-view-get", methods=["GET"])
api.add_resource(AuthProfileView, '/api/auth-profile-view/create',endpoint="api-auth-profile-view-post", methods=["POST"])
api.add_resource(AuthProfileView, '/api/auth-profile-view/update/<int:id>',endpoint="api-auth-profile-view-update", methods=["PUT"])
api.add_resource(AuthProfileViewSearch, '/api/auth-profile-view/get',endpoint="api-auth-profile-view-get-all", methods=["GET"])
api.add_resource(AuthProfileViewRole,'/api/auth-profile-view/add-role-by-endpoint',endpoint="api-auth-profile-view-post-role-by-endpoint", methods=["POST"])