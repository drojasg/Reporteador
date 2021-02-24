from config import api
from .booking import BookingPublic, Booking, BookingSearch, Confirmation, Pms, BookingSearchTotal,\
ConfirmationPublic, BookingCancel, BookingPublicValidate
from .booking_v2 import BookingPublicV2
from .booking_process import BookingOnHoldReminder, BookingOnHoldCancel
from .book_test_api import test_book_apis, request_to_pms
from .booking_operation import BookingOperation, BookHotelRoomUpdatePax, BookHotelUpdateCreationModDate
#from .booking_canceled import BookingCanceledLetter, BookingModificationLetter

#urls apis basicas
api.add_resource(BookingPublic, '/api/public/booking/create', endpoint="api-public-booking-post", methods=["POST"])
api.add_resource(BookingPublic, '/api/public/booking/<string:code_reservation>', endpoint="api-public-booking-put", methods=["PUT"])
api.add_resource(BookingPublic, '/api/public/booking/<string:code_reservation>/<string:full_name>', endpoint="api-public-booking-get", methods=["GET"])
api.add_resource(ConfirmationPublic, '/api/public/confirmation', endpoint="api-public-confirmation-post", methods=["POST"])
api.add_resource(BookingPublicValidate, '/api/public/validate/booking/create', endpoint="api-public-validate-booking-post", methods=["POST"])

api.add_resource(BookingPublicV2, '/api/public/v2/booking/<string:code_reservation>/<string:full_name>/<string:lang_code>', endpoint="api-public-v2-booking-get", methods=["GET"])

api.add_resource(BookingSearch, '/api/booking/get/<int:iddef_property>/<int:idbook_status>/<string:code_book_hotel>/<string:from_date_travel>/<string:to_date_travel>/<string:from_date_booking>/<string:to_date_booking>/<int:limit>/<int:offset>',endpoint="api-booking-get-all", methods=["GET"])
api.add_resource(BookingSearchTotal, '/api/booking/count/<int:iddef_property>/<int:idbook_status>/<string:code_book_hotel>/<string:from_date_travel>/<string:to_date_travel>/<string:from_date_booking>/<string:to_date_booking>',endpoint="api-booking-get-count", methods=["GET"])
api.add_resource(Booking, '/api/booking/get/<int:id>',endpoint="api-booking-get", methods=["GET"])
api.add_resource(Confirmation, '/api/booking/send-confirmation/<int:id>',endpoint="api-booking-send-confirmation", methods=["POST"])
api.add_resource(Pms, '/api/booking/send-pms/<int:id>',endpoint="api-booking-send-pms", methods=["POST"])
api.add_resource(test_book_apis, '/api/test/book_wire/<int:idbook>',endpoint="api-test-booking-send-pms", methods=["get"])
api.add_resource(BookingOperation, '/api/booking/change/<string:code_reservation>', endpoint="api-booking-change", methods=["PUT"])
api.add_resource(BookHotelRoomUpdatePax, '/api/booking/room_pax/update', endpoint="api-booking-room-pax-put", methods=["PUT"])
api.add_resource(BookHotelUpdateCreationModDate, '/api/booking/create_date/update', endpoint="api-booking-create-mod-date-put", methods=["PUT"])

api.add_resource(BookingOnHoldReminder, '/api/booking/on-hold-reminder',endpoint="api-booking-on-hold-reminder", methods=["post"])
api.add_resource(BookingOnHoldCancel, '/api/booking/on-hold-cancel',endpoint="api-booking-on-hold-cancel", methods=["post"])
api.add_resource(BookingCancel, '/api/booking/cancel-confirmation',endpoint="api-booking-send-cancel", methods=["POST"])
api.add_resource(request_to_pms, '/api/booking/pms_request/get/<int:id>',endpoint="api-booking-get-pms", methods=["GET"])

#api.add_resource(BookingCanceledLetter, '/api/booking/canceled-letter/<string:code_reservation>',endpoint="api-booking-canceled-letter", methods=["POST"])
#api.add_resource(BookingModificationLetter, '/api/booking/modification-letter/<string:code_reservation>',endpoint="api-booking-modification-letter", methods=["POST"])
#api.add_resource(Pms, '/api/booking/send-pms/<int:id>',endpoint="api-booking-send-pms", methods=["POST"])