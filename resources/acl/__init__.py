from config import api
from .acl import Acl

#urls apis basicas
api.add_resource(Acl, '/api/acl/<string:controller>/<string:method>',endpoint="api-acl-get", methods=["GET"])