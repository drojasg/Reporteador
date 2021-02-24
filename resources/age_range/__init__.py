from config import api
from .age_range import AgeRangePropetyListSearch,\
AgeRangeListSearch, AgeRangeStatus, AgeRangePropetySearch, \
AgeRange, AgeRangeListSearchEnglish, AgeProperty_V2

#urls apis basicas
api.add_resource(AgeRange, '/api/age-range/create',endpoint="api-age-range-post", methods=["POST"])
api.add_resource(AgeRange, '/api/age-range/search/<int:id>',endpoint="api-age-range-get-by-id", methods=["GET"])
api.add_resource(AgeRange, '/api/age-range/update/<int:id>',endpoint="api-age-range-put", methods=["PUT"])
api.add_resource(AgeRangeStatus, '/api/age-range/delete/<int:id>/<int:status>',endpoint="api-age-range-delete", methods=["PUT"])
api.add_resource(AgeRangeListSearch, '/api/age-range/get',endpoint="api-age-range-get-all", methods=["GET"])
api.add_resource(AgeRangePropetyListSearch, '/api/age-range-propety/search/<int:id>',endpoint="api-age-range-propety-get-all", methods=["GET"])
api.add_resource(AgeRangeListSearchEnglish, '/api/age-range/get-in-english',endpoint="api-age-range-get-all-english", methods=["GET"])

#Apis publicas
api.add_resource(AgeRangePropetySearch, '/api/public/age-range-propety/search/<string:property_code>/<string:lang_code>', endpoint='api-public-age-range-property-get-by-id-property', methods=["GET"])
api.add_resource(AgeProperty_V2, '/api/v2/public/age-range-propety/search/<string:property_code>', endpoint='api-v2-public-age-range-property-get-by-id-property', methods=["GET"])