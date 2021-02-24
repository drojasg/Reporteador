from config import api
from .media_property_desc import MediaPropertyDescListSearch

api.add_resource(MediaPropertyDescListSearch, '/api/media-property-desc/search-all-by-property/<int:idProperty>/<int:idDescType>/<int:idDefMediaType>',endpoint="api-media-get-all-by-property", methods=["GET"])
api.add_resource(MediaPropertyDescListSearch, '/api/media-property-desc/post-and-put-media',endpoint="api-media-property-desc-post-and-put", methods=["POST"])