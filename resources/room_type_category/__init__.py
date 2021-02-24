from config import api
from .room_type_category import RoomTypeCategoryListSearch, \
RoomTypeCategory, RoomTypesRateplan, RoomTypeCategorySingle, \
RoomTypeCategoryDefaultList, publicRoomTypeDetail, RoomTypeForPropertyToRatePlan,\
RoomTypesProperty, RoomTypeCategoryCodeOpera

#urls apis basicas
api.add_resource(RoomTypeCategory, '/api/room-type-category/create',endpoint="api-room-type-category-post", methods=["POST"])
api.add_resource(RoomTypeCategory, '/api/room-type-category/search/<int:id>',endpoint="api-room-type-category-get-by-id", methods=["GET"])
api.add_resource(RoomTypeCategory, '/api/room-type-category/update/<int:id>',endpoint="api-room-type-category-put", methods=["PUT"])
api.add_resource(RoomTypeCategory, '/api/room-type-category/delete/<int:id>',endpoint="api-room-type-category-delete", methods=["DELETE"])
api.add_resource(RoomTypeCategoryListSearch, '/api/room-type-category/get',endpoint="api-room-type-category-get-all", methods=["GET"])
api.add_resource(RoomTypeCategoryListSearch, '/api/room-type-category/create/room',endpoint="api-room-type_category-post-list", methods=["POST"])
api.add_resource(RoomTypeCategoryListSearch, '/api/room-type-category/update/room/<int:roomtype>',endpoint="api-room-type_category-put-list", methods=["PUT"])
api.add_resource(RoomTypesRateplan, '/api/room-type-category/rate-plan/get/<int:id_property>/<int:id_rateplan>',endpoint="api-room-type-category-rateplan-get-all", methods=["GET"])
api.add_resource(RoomTypeCategorySingle, '/api/room-type-category/get/single',endpoint="api-room-type-category-single-get", methods=["GET"])
api.add_resource(RoomTypeCategoryDefaultList, '/api/room-type-category/get/list',endpoint="api-room-type-category-list-get", methods=["GET"])
api.add_resource(RoomTypeForPropertyToRatePlan, '/api/room-type_category/get/list/property/<int:propertyId>/<int:rateplanId>', endpoint='api-get-room-type-category-to-rateplan',methods=["GET"])
api.add_resource(RoomTypesProperty, '/api/room-type-category/property/get/<string:property_code>', endpoint='api-get-room-type-category-to-property',methods=["GET"])
api.add_resource(RoomTypeCategoryCodeOpera, '/api/room-type-category/room-opera', endpoint='api-room-type-category-code-get',methods=["POST"])

#Apis publicas
api.add_resource(publicRoomTypeDetail,'/api/public/room-type-category/get/detail',endpoint="api-public-room-type-category-detail-post", methods=["POST"])