from config import api
from .media_service import MediaService,MediaServiceListSearch, AdminMediaServiceList

#urls apis basicas
#Administrativas
api.add_resource(MediaService, '/api/media-service/create',endpoint="api-media-service-post", methods=["POST"])
api.add_resource(MediaService, '/api/media-service/search/<int:id>',endpoint="api-media-service-get-by-id", methods=["GET"])
api.add_resource(MediaService, '/api/media-service/update/<int:id>',endpoint="api-media-service-put", methods=["PUT"])
api.add_resource(MediaService, '/api/media-service/delete/<int:id>',endpoint="api-media-service-delete", methods=["DELETE"])
api.add_resource(MediaServiceListSearch, '/api/media-service/get',endpoint="api-media-service-get-all", methods=["GET"])
api.add_resource(AdminMediaServiceList, '/api/media-service/search-by-service-langcode/<int:idService>/<string:langCode>/<int:idProperty>/<int:idDefMediaType>',endpoint="api-admin-media-service-get-all", methods=["GET"])
api.add_resource(AdminMediaServiceList, '/api/media-service/post-and-put-media',endpoint="api-media-service-post-and-put", methods=["POST"])