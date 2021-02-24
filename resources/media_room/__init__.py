from config import api
from .media_room import AdminMediaRoomList, AdminMediaRoomListOrder

api.add_resource(AdminMediaRoomList, '/api/media-room/search-by-roomtype/<int:idRoomType>/<int:idProperty>',endpoint="api-media-room-get-by-roomtype", methods=["GET"])
api.add_resource(AdminMediaRoomList, '/api/media-room/post-and-put-media',endpoint="api-media-room-post-and-put", methods=["POST"])
api.add_resource(AdminMediaRoomListOrder, '/api/media-room/update-order-media', endpoint="api-media-room-update-media", methods=["PUT"])
api.add_resource(AdminMediaRoomListOrder, '/api/media-room/search-order-by-roomtype/<int:idRoomType>/<int:idMediaType>', endpoint="api-media-room-seach-order-by-roomtype", methods=["GET"])