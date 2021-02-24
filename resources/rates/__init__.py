from config import api
from .rates import Rates_Detail
from .calendar_rates import CalendarRates,PublicRates, Promotions
from .public_rates import PublicRates_v2, PublicDiscounts, InternalRates_v2
from .push_rates import Push

api.add_resource(CalendarRates, '/api/rates/calendar',endpoint="api-rates-prices-get-calendar", methods=["POST"])
api.add_resource(Push, '/api/rates/push-rates', endpoint="api-rates-push-rates", methods=['POST'])
api.add_resource(Promotions, '/api/promotions/get',endpoint="api-promo-test", methods=["POST"])
#api.add_resource(RatePlanPricesListSearch, '/api/rates-prices/get',endpoint="api-brrates-pricesand-get-all", methods=["GET"])

#Apis publicas
api.add_resource(Rates_Detail, '/api/public/rates/create',endpoint="api-public-push-rates-post", methods=["POST"])
api.add_resource(PublicRates, '/api/public/rates/get',endpoint="api-public-rates-post", methods=["POST"])

#Apis v2
api.add_resource(PublicRates_v2, '/api/v2/public/rates/property/get/<string:hotel_code>/<string:country>/<string:currency>',endpoint="api-v2-public-property-rates", methods=["GET"])
api.add_resource(PublicRates_v2, '/api/v2/public/rates/room/get',endpoint="api-v2-public-room-rates", methods=["POST"])
api.add_resource(PublicDiscounts, '/api/v2/public/rates/room/quote',endpoint="api-v2-public-room-quote", methods=["POST"])
api.add_resource(InternalRates_v2, '/api/v2/internal/rates/room/get',endpoint="api-v2-internal-room-rates", methods=["POST"])