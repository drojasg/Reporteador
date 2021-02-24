from config import api
from .email_contact import EmailContactListSearch, EmailContact

#urls apis basicas
api.add_resource(EmailContact, '/api/email-contact/create',endpoint="api-email-contact-post", methods=["POST"])
api.add_resource(EmailContact, '/api/email-contact/search/<int:id>',endpoint="api-email-contact-get-by-id", methods=["GET"])
api.add_resource(EmailContact, '/api/email-contact/update/<int:id>',endpoint="api-email-contact-put", methods=["PUT"])
api.add_resource(EmailContact, '/api/email-contact/delete/<int:id>',endpoint="api-email-contact-delete", methods=["DELETE"])
api.add_resource(EmailContactListSearch, '/api/email-contact/get',endpoint="api-email-contact-get-all", methods=["GET"])