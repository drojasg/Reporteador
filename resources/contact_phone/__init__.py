from config import api
from .contact_phone import ContactPhoneListSearch, ContactPhone

#urls apis basicas
api.add_resource(ContactPhone, '/api/contact-phone/create',endpoint="api-contact-phone-post", methods=["POST"])
api.add_resource(ContactPhone, '/api/contact-phone/search/<int:id>',endpoint="api-contact-phone-get-by-id", methods=["GET"])
api.add_resource(ContactPhone, '/api/contact-phone/update/<int:id>',endpoint="api-contact-phone-put", methods=["PUT"])
api.add_resource(ContactPhone, '/api/contact-phone/delete/<int:id>',endpoint="api-contact-phone-delete", methods=["DELETE"])
api.add_resource(ContactPhoneListSearch, '/api/contact-phone/get',endpoint="api-contact-phone-get-all", methods=["GET"])