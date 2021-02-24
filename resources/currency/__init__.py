from config import api
from .currency import Currency, CurrencyListSearch, CurrencyList, CurrencyLangList, CurrencyUpdateStatus

#urls apis basicas
api.add_resource(Currency, '/api/currency/create',endpoint="api-currency-post", methods=["POST"])
api.add_resource(Currency, '/api/currency/search/<int:id>',endpoint="api-currency-get-by-id", methods=["GET"])
api.add_resource(Currency, '/api/currency/update/<int:id>',endpoint="api-currency-put", methods=["PUT"])
api.add_resource(Currency, '/api/currency/delete/<int:id>',endpoint="api-currency-delete", methods=["DELETE"])
api.add_resource(CurrencyListSearch, '/api/currency/get',endpoint="api-currency-get-all", methods=["GET"])
api.add_resource(CurrencyUpdateStatus, '/api/currency/update-status/<int:id>',endpoint="api-currency-update-status", methods=["PUT"])
#public
api.add_resource(CurrencyList, '/api/public/currency/get',endpoint="api-public-currency-get-all", methods=["GET"])
api.add_resource(CurrencyLangList, '/api/public/currency/get/<string:lang_code>',endpoint="api-public-currency-lang-get-all", methods=["GET"])