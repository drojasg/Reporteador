from config import api
from .time_zone import TimeZoneListSearch, TimeZoneStatus, TimeZone

#urls apis basicas
api.add_resource(TimeZone, '/api/time-zone/create',endpoint="api-time-zone-post", methods=["POST"])
api.add_resource(TimeZone, '/api/time-zone/search/<int:id>',endpoint="api-time-zone-get-by-id", methods=["GET"])
api.add_resource(TimeZone, '/api/time-zone/update/<int:id>',endpoint="api-time-zone-put", methods=["PUT"])
api.add_resource(TimeZoneStatus, '/api/time-zone/delete/<int:id>/<int:status>',endpoint="api-time-zone-update-status", methods=["PUT"])
api.add_resource(TimeZoneListSearch, '/api/time-zone/get',endpoint="api-time-zone-get-all", methods=["GET"])