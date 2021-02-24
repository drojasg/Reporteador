from config import api
from .media_group import MediaGroupListSearch, MediaGroup, MediaGroupGalleryListSearch, MediaGroupGalleryCountSearch, MediaGroupGalleryAssetsSearch, MediaGeneralSearch

#urls apis basicas
api.add_resource(MediaGroup, '/api/media-group/create',endpoint="api-media-group-post", methods=["POST"])
api.add_resource(MediaGroup, '/api/media-group/search/<int:id>',endpoint="api-media-group-get-by-id", methods=["GET"])
api.add_resource(MediaGroup, '/api/media-group/update/<int:id>',endpoint="api-media-group-put", methods=["PUT"])
api.add_resource(MediaGroup, '/api/media-group/delete/<int:id>',endpoint="api-media-group-delete", methods=["DELETE"])
api.add_resource(MediaGroupListSearch, '/api/media-group/get',endpoint="api-media-group-get-all", methods=["GET"])
api.add_resource(MediaGroupGalleryListSearch, '/api/media-group/get-all-gallery/<int:id>',endpoint="api-media-group-get-all-gallery", methods=["GET"])
api.add_resource(MediaGroupGalleryCountSearch, '/api/media-group/get-count-group/<int:id>',endpoint="api-media-group-get-count-group", methods=["GET"])
api.add_resource(MediaGroupGalleryAssetsSearch, '/api/media-group/get-all-media-by-group/<int:idGroup>/<int:Nlimit>/<int:Noffset>',endpoint="api-media-group-get-all-media-by-group", methods=["GET"])
api.add_resource(MediaGroupGalleryAssetsSearch, '/api/media-group/update-media-gallery-status/<int:id>',endpoint="api-media-group-update-status", methods=["PUT"])
api.add_resource(MediaGeneralSearch, '/api/media-general-search',endpoint="api-media-general-get", methods=["POST"])