from config import api
from .booking_customer import BookCustomerModify as customer
from .booking_rooms import BookRoomsModify as rooms
from .booking import BookingModify as booking
from .service import BookingServiceModify as service
from .booking_rates import BookingModifyRates as rates, BookingModifiRateplan as rateplan,\
BookingModifyCalculate as quote, BookingRoomRatesInfo as rates_info, BookingModifyCalculatePayment as book_payment
from .booking_comment import BookingCommentModify as comment
from .booking_promo_code import BookingPromoCodeModify as promocode

api.add_resource(customer,'/api/internal/booking/customer/<int:idbooking>', endpoint="api-internal-booking-customer-post", methods=["GET"])
api.add_resource(rooms,'/api/internal/booking/rooms/<int:idbooking>', endpoint="api-internal-booking-rooms-post", methods=["GET"])
api.add_resource(rooms,'/api/internal/booking/rooms/get', endpoint="api-internal-booking-rooms-get", methods=["POST"])
api.add_resource(booking,'/api/internal/booking/<int:idbooking>', endpoint="api-internal-booking", methods=["GET"])
api.add_resource(service,'/api/internal/booking/service/<int:idbooking>', endpoint="api-internal-booking-services-get", methods=["GET"])
api.add_resource(rates,'/api/internal/booking/rates/', endpoint="api-internal-booking-rates-get", methods=["POST"])
api.add_resource(service,'/api/internal/booking/service', endpoint="api-internal-booking-services-post", methods=["POST"])
api.add_resource(comment,'/api/internal/booking/comment/<int:idbooking>', endpoint="api-internal-booking-comment-get", methods=["GET"])
api.add_resource(promocode,'/api/internal/booking/promocode/<int:idbooking>', endpoint="api-internal-booking-promocode-get", methods=["GET"])
api.add_resource(promocode,'/api/internal/booking/promocode', endpoint="api-internal-booking-promocode-post", methods=["POST"])
api.add_resource(rateplan,'/api/internal/booking/rateplan', endpoint="api-internal-booking-rateplan-post", methods=["POST"])
api.add_resource(quote,'/api/internal/booking/rates/quote', endpoint="api-internal-booking-rates-quote-post", methods=["POST"])
api.add_resource(rates_info,'/api/internal/booking/room-rates/<int:idbook_hotel_room>', endpoint="api-booking-room-rates-info-get", methods=["GET"])
api.add_resource(book_payment,'/api/internal/booking/rates/payment/<int:idbook_hotel>', endpoint="api-internal-booking-payment-get", methods=["GET"])