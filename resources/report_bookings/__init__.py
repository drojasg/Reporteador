from config import api
from .report_bookings import reportBookings


api.add_resource(reportBookings, '/api/reports/get-booking-report',endpoint="api-reports-get-report", methods=["POST"])