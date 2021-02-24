from config  import api
from .policy_payment import PolicyPayment, PolicyPaymentStatus, PolicyPaymentListSearch,PolicyPaymentPublic, PolicyPaymentPublicV2

api.add_resource(PolicyPayment, '/api/policy_payment/post',endpoint="api-policy_payment-create", methods=["POST"])
api.add_resource(PolicyPayment, '/api/policy_payment/put/<int:id>',endpoint="api-policy_payment-update", methods=["PUT"])
api.add_resource(PolicyPayment, '/api/policy_payment/get',endpoint="api-policy_payment-get-all", methods=["GET"])
api.add_resource(PolicyPaymentStatus, '/api/policy_payment/change_status/<int:id>/<int:estado>',endpoint="api-policy_payment-change-status", methods=["PUT"])
api.add_resource(PolicyPaymentListSearch, '/api/policy_payment/get/<int:id>',endpoint="api-policy_payment-get-id", methods=["GET"])

#APIS-PUBLICAS
api.add_resource(PolicyPaymentPublic, '/api/public/payment-terms/get/<string:country_code>/<string:lang>/<string:property_code>',endpoint="api-public-payment-terms-get-text", methods=["GET"])
#api v2
api.add_resource(PolicyPaymentPublicV2, '/api/public/payment-terms-v2/get/<string:country_code>/<string:lang>/<string:property_code>',endpoint="api-public-payment-v2-terms-get-text", methods=["GET"])
