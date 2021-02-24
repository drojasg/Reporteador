from config import api
from .permission import PermissionPublic

#urls apis basicas
api.add_resource(PermissionPublic, '/api/public/permission/verify',endpoint="api-public-permission-post", methods=["POST"])