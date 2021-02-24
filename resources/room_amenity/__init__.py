from config import api
from .room_amenity import RoomAmenityListSearch, RoomAmenity, ListRoomAmenity,RoomAmenityDescriptions

#urls apis basicas
api.add_resource(RoomAmenity, '/api/room-amenity/create',endpoint="api-room-amenity-post", methods=["POST"])
api.add_resource(RoomAmenity, '/api/room-amenity/search/<int:id>',endpoint="api-room-amenity-get-by-id", methods=["GET"])
api.add_resource(RoomAmenity, '/api/room-amenity/update/<int:id>',endpoint="api-room-amenity-put", methods=["PUT"])
api.add_resource(RoomAmenity, '/api/room-amenity/delete/<int:id>',endpoint="api-room-amenity-delete", methods=["DELETE"])
api.add_resource(RoomAmenityListSearch, '/api/room-amenity/get',endpoint="api-room-amenity-get-all", methods=["GET"])
api.add_resource(ListRoomAmenity, '/api/room-amenity/get/<int:idProperty>/<int:idRoom>',endpoint="api-room-amenity-get-parameters", methods=["GET"])
api.add_resource(RoomAmenityDescriptions, '/api/room-amenity/get/room-amenity-descriptions/<int:iddef_room_type_category>/<string:lang_code>',endpoint="api-room-amenity-get-room-amenity-descriptions", methods=["GET"])