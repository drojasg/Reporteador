from config import api
from .payment import Validation, Payment, PaymentSearch, LinkPayments, BookingInfoTransactionId, BookingInfoTransactionCode

#urls apis basicas
api.add_resource(Validation, '/api/public/card/validation',endpoint="api-public-card-post", methods=["POST"])
#api.add_resource(Payment, '/api/public/payment',endpoint="api-payment-post", methods=["POST"])
api.add_resource(PaymentSearch, '/api/payments/<int:idbook_hotel>',endpoint="api-payment-search-get", methods=["GET"])
api.add_resource(LinkPayments, '/api/payments/link-payments',endpoint="api-link-payments-post", methods=["POST"])
api.add_resource(LinkPayments, '/api/payments/link-payments/test',endpoint="api-link-payments-get", methods=["GET"])
api.add_resource(BookingInfoTransactionId, '/api/payments/total_transactions/<int:idbook_hotel>',endpoint="api-total-transactions-id-get", methods=["GET"])
api.add_resource(BookingInfoTransactionCode, '/api/payments/total_transactions_code/<string:code_reservation>',endpoint="api-total-transactions-code-get", methods=["GET"])
