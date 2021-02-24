from config import api
from .terms_and_conditions import TermsAndConditions, TermsAndConditionsListSearch, TermsAndConditionsList, TermsAndConditionsPublic, TermsAndConditionsBrandPublic

#urls apis basicas
#Administrativas
api.add_resource(TermsAndConditions, '/api/terms-and-conditions/create',endpoint="api-terms-and-conditions-post", methods=["POST"])
api.add_resource(TermsAndConditions, '/api/terms-and-conditions/search-id/<int:id>',endpoint="api-terms-and-conditions-get-by-id", methods=["GET"])
api.add_resource(TermsAndConditionsListSearch, '/api/terms-and-conditions/search-all/',endpoint="api-terms-and-conditions-get-all", methods=["GET"])
api.add_resource(TermsAndConditions, '/api/terms-and-conditions/update/<int:id>',endpoint="api-terms-and-conditions-put", methods=["PUT"])
api.add_resource(TermsAndConditions, '/api/terms-and-conditions/delete/<int:id>',endpoint="api-terms-and-conditions-delete", methods=["DELETE"])
api.add_resource(TermsAndConditionsList, '/api/terms-and-conditions/get-by-brand/<int:id>',endpoint="api-terms-and-conditions-get-by-brand", methods=["GET"])

api.add_resource(TermsAndConditionsPublic, '/api/public/terms-and-conditions/get/<string:property_code>/<string:lang_code>',endpoint="api-public-terms-get", methods=["GET"])
api.add_resource(TermsAndConditionsBrandPublic, '/api/public/terms-and-conditions/brand/get/<string:brand_code>/<string:lang_code>',endpoint="api-public-terms-brand-get", methods=["GET"])