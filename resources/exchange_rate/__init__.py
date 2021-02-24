from config import api
from .exchange_rate import ExchangeRate,ExchangeRateOpenEx

#urls apis basicas
""" api.add_resource(ExchangeRate, '/api/exchange-rate/load', endpoint="api-exchange-rate-post", methods=["POST"]) """
api.add_resource(ExchangeRateOpenEx, '/api/exchange-rate/load', endpoint="api-exchange-rate-openex-post", methods=["POST"])
api.add_resource(ExchangeRate, '/api/exchange-rate/layer/<string:currency_code>', endpoint="api-exchange-rate-get", methods=["GET"])