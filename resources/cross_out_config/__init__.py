from config import api
from .cross_out_config import CrossOutConfigList,CrossOutConfigListSearch, CrossOutConfig, GetExternalCrossout

#urls apis basicas
api.add_resource(CrossOutConfig, '/api/crossout/create',endpoint="api-cross-out-config-post", methods=["POST"])
api.add_resource(CrossOutConfig, '/api/crossout/search/<int:id>',endpoint="api-cross-out-config-get-by-id", methods=["GET"])
api.add_resource(CrossOutConfig, '/api/crossout/update/<int:id>',endpoint="api-cross-out-config-put", methods=["PUT"])
api.add_resource(CrossOutConfig, '/api/crossout/delete/<int:id>',endpoint="api-cross-out-config-delete", methods=["DELETE"])
api.add_resource(CrossOutConfigListSearch, '/api/crossout/get',endpoint="api-cross-out-config-get-all", methods=["GET"])

#Url funcionalidades
api.add_resource(CrossOutConfigList, '/api/crossout/search-rate-plan',endpoint="api-cross-out-config-post-all", methods=["POST"])

#Url para sistemas externos
api.add_resource(GetExternalCrossout, '/api/external/crossouts/get',endpoint="api-cross-out-config-post-ext", methods=["POST"])