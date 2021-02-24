from config import api
from .sistemas import Sistemas, SistemasSearch

#urls apis basicas
api.add_resource(Sistemas, '/api/sistems/create',endpoint="api-sistems-post", methods=["POST"])
api.add_resource(Sistemas, '/api/sistems/search/<int:id>',endpoint="api-csistems-get-by-id", methods=["GET"])
api.add_resource(Sistemas, '/api/sistems/update/<int:id>',endpoint="api-sistems-put", methods=["PUT"])
api.add_resource(Sistemas, '/api/sistems/delete/<int:id>',endpoint="api-sistems-delete", methods=["DELETE"])
api.add_resource(SistemasSearch, '/api/sistems/get',endpoint="api-sistems-get-all", methods=["GET"])
api.add_resource(SistemasSearch, '/api/sistems/update-status/<int:id>',endpoint="api-sistems-update-status", methods=["PUT"])