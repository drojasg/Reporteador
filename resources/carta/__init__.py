from config import api
from .carta import CartaPdf
from .emailTemplate import EmailTemplate

api.add_resource(CartaPdf, '/api/card/get-confirmation/<string:code_reservation>/<string:full_name>/<string:language_code>',endpoint="api-public-get-card", methods=["GET"])
api.add_resource(EmailTemplate, '/api/card/emailtemplate',endpoint="api-public-get-email", methods=["GET"])
api.add_resource(CartaPdf, '/api/card/post-upload-confirmation',endpoint="api-upload-confirmation", methods=["POST"])
