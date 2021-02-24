from config import api
from .payment_method import PaymentMethod, PaymentMethodList

api.add_resource(PaymentMethod, '/api/payment-method/create',endpoint="api-payment-method-post", methods=["POST"])
api.add_resource(PaymentMethod, '/api/payment-method/search/<int:id>',endpoint="api-payment-method-get-by-id", methods=["GET"])
api.add_resource(PaymentMethod, '/api/payment-method/update/<int:id>',endpoint="api-payment-method-put", methods=["PUT"])
api.add_resource(PaymentMethodList, '/api/payment-method/get',endpoint="api-payment-method-get-all", methods=["GET"])