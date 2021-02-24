from config import api
from .media_type import MediaTypeListSearch, MediaType, MediaTypeGalleryListSearch

#urls apis basicas
api.add_resource(MediaType, '/api/media-type/create',endpoint="api-media-type-post", methods=["POST"])
api.add_resource(MediaType, '/api/media-type/search/<int:id>',endpoint="api-media-type-get-by-id", methods=["GET"])
api.add_resource(MediaType, '/api/media-type/update/<int:id>',endpoint="api-media-type-put", methods=["PUT"])
api.add_resource(MediaType, '/api/media-type/delete/<int:id>',endpoint="api-media-type-delete", methods=["DELETE"])
api.add_resource(MediaTypeListSearch, '/api/media-type/get',endpoint="api-media-type-get-all", methods=["GET"])
api.add_resource(MediaTypeGalleryListSearch, '/api/media-type/get-all-gallery', endpoint="api-media-type-get-all-gallery", methods=["GET"])