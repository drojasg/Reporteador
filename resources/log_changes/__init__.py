from config import api
from .log_changes import LogChanges, LogChangesBooking

#Basic APIs
api.add_resource(LogChanges, '/api/log-changes/search/<string:table>/<int:id>', endpoint="api-log-changes-get", methods=["GET"])
api.add_resource(LogChangesBooking, '/api/log-changes/booking/<string:code_reservation>', endpoint="api-log-changes-booking-get", methods=["GET"])