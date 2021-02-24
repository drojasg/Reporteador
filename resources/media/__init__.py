from config import api
from .media import MediaListSearch, Media,MediaGalleryList, MediaUpdateUrl

#urls apis basicas
api.add_resource(Media, '/api/media/create',endpoint="api-media-post", methods=["POST"])
api.add_resource(Media, '/api/media/search/<int:id>',endpoint="api-media-get-by-id", methods=["GET"])
api.add_resource(Media, '/api/media/update/<int:id>',endpoint="api-media-put", methods=["PUT"])
api.add_resource(Media, '/api/media/delete/<int:id>',endpoint="api-media-delete", methods=["DELETE"])
api.add_resource(MediaListSearch, '/api/media/get',endpoint="api-media-get-all", methods=["GET"])
api.add_resource(MediaGalleryList, '/api/media/update-media-gallery-status/<int:id>',endpoint="api-media-update-status", methods=["PUT"])
api.add_resource(MediaUpdateUrl, '/api/media/update-media-url/<int:id>',endpoint="api-media-update-url", methods=["PUT"])