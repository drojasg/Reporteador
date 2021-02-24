from config import api
from .config_booking import ConfigBooking, ConfigBookingListSearch, ConfigBookingPublic

api.add_resource(ConfigBooking, '/api/config_booking/search/<int:id>',endpoint="api-config-booking-get-by-id", methods=["GET"])
api.add_resource(ConfigBooking, '/api/config_booking/create',endpoint="api-config-booking-create", methods=["POST"])
api.add_resource(ConfigBooking, '/api/config_booking/update/<int:id>',endpoint="api-config-booking-update", methods=["PUT"])
api.add_resource(ConfigBookingListSearch, '/api/config_booking/search-all',endpoint="api-config-booking-search-list", methods=["GET"])
api.add_resource(ConfigBookingListSearch, '/api/config_booking/delete-status/<int:id>',endpoint="api-config-booking-delete-status", methods=["PUT"])

api.add_resource(ConfigBookingPublic, '/api/public/config_booking/get/<string:lang>',endpoint="api-public-config-booking-get", methods=["GET"])