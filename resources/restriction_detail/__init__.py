from config import api
from .restriction_detail import RestrictionDetail, RestrictionDetailRoomRateplan, Test

#urls apis basicas
api.add_resource(RestrictionDetail, '/api/restriction-detail/get/<int:id>',endpoint="api-restrictiondetail-get-all", methods=["GET"])
api.add_resource(RestrictionDetailRoomRateplan, '/api/restriction-detail/get-closedates', endpoint="api-restrictiondetail-get-closedates", methods=["POST"])
api.add_resource(Test, '/api/restriction-detail/test',endpoint="api-restrictiondetail-test", methods=["GET"])
