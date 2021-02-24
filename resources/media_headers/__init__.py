from config import api
from .media_headers import MediaHeaders, MediaHeadersList, headersPublic

api.add_resource(MediaHeaders, '/api/media-headers/get/<int:id>', endpoint="api-media-headers-get-by-id", methods=["GET"])
api.add_resource(MediaHeaders, '/api/media-headers/create', endpoint="api-media-headers-create", methods=["POST"])
api.add_resource(MediaHeaders, '/api/media-headers/update', endpoint="api-media-headers-update", methods=["PUT"])
api.add_resource(MediaHeadersList, '/api/media-headers/get-all', endpoint="api-media-headers-get-all", methods=["GET"])
api.add_resource(MediaHeadersList, '/api/media-headers/update-status', endpoint="api-media-headers-update-status", methods=["PUT"])
api.add_resource(headersPublic, '/api/public/media-headers/get/<string:property_code>/<string:brand_code>/<string:lang_code>', endpoint="api-public-media-headers-get", methods=["GET"])