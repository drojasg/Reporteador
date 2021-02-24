from config import api
from .country import Country,CountryListSearch,CountryLang

#urls apis basicas
api.add_resource(Country, '/api/country/create',endpoint="api-country-post", methods=["POST"])
api.add_resource(Country, '/api/country/search/<int:id>',endpoint="api-country-get-by-id", methods=["GET"])
api.add_resource(Country, '/api/country/update/<int:id>',endpoint="api-country-put", methods=["PUT"])
api.add_resource(Country, '/api/country/delete/<int:id>',endpoint="api-country-delete", methods=["DELETE"])
api.add_resource(CountryListSearch, '/api/country/get',endpoint="api-country-get-all", methods=["GET"])

#Apis publicas
api.add_resource(CountryLang, '/api/public/country-lang/get/<string:lang_code>',endpoint="api-public-country-lang", methods=["GET"])