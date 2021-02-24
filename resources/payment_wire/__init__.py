from config import api
from .wire_payment import PaymentWire

api.add_resource(PaymentWire, '/api/test/paymentwire',endpoint="api-public-payment-test", methods=["GET"])