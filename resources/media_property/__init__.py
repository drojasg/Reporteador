from config import api
from .media_property import MediaProperty,MediaPropertyListSearch,PublicMediaProperty,PublicMediaPropertyList, AdminMediaPropertyList,MediaPropertyListOrder

#urls apis basicas
#Administrativas
api.add_resource(MediaProperty, '/api/media-property/create',endpoint="api-media-property-post", methods=["POST"])
api.add_resource(MediaProperty, '/api/media-property/search/<int:id>',endpoint="api-media-property-get-by-id", methods=["GET"])
api.add_resource(MediaProperty, '/api/media-property/update/<int:id>',endpoint="api-media-property-put", methods=["PUT"])
api.add_resource(MediaProperty, '/api/media-property/delete/<int:id>',endpoint="api-media-property-delete", methods=["DELETE"])
api.add_resource(MediaPropertyListSearch, '/api/media-property/get',endpoint="api-media-property-get-all", methods=["GET"])
api.add_resource(AdminMediaPropertyList, '/api/media-property/search-all-by-property/<int:idProperty>/<int:idDefMediaType>',endpoint="api-media-property-get-list", methods=["GET"])
api.add_resource(AdminMediaPropertyList, '/api/media-property/post-and-put-media',endpoint="api-media-property-post-and-put", methods=["POST"])
api.add_resource(MediaPropertyListOrder, '/api/media-property/update-order-media', endpoint="api-media-property-update-media", methods=["PUT"])
api.add_resource(MediaPropertyListOrder, '/api/media-property/search-order-by-property/<int:idProperty>', endpoint="api-media-property-seach-order-by-property", methods=["GET"])

#Publicas
api.add_resource(PublicMediaProperty, '/api/public/media-property/search/<int:id>',endpoint="api-public-media-property-get-by-id", methods=["GET"])
api.add_resource(PublicMediaPropertyList, '/api/public/media-property/search/property/<int:id>',endpoint="api-public-media-property-get-list", methods=["GET"])