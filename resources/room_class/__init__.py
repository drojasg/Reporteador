from config import api
from .room_class import RoomClassListSearch, RoomClass

#urls apis basicas
api.add_resource(RoomClass, '/api/room-class/create',endpoint="api-room-class-post", methods=["POST"])
api.add_resource(RoomClass, '/api/room-class/search/<int:id>',endpoint="api-room-class-get-by-id", methods=["GET"])
api.add_resource(RoomClass, '/api/room-class/update/<int:id>',endpoint="api-room-class-put", methods=["PUT"])
api.add_resource(RoomClass, '/api/room-class/delete/<int:id>',endpoint="api-room-class-delete", methods=["DELETE"])
api.add_resource(RoomClassListSearch, '/api/room-class/get',endpoint="api-room-class-get-all", methods=["GET"])