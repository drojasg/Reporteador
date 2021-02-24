from config import api
from .contact_type import ContactTypeListSearch, ContactType

#urls apis basicas
api.add_resource(ContactType, '/api/contact-types/create',endpoint="api-contact-types-post", methods=["POST"])
api.add_resource(ContactType, '/api/contact-types/search/<int:id>',endpoint="api-contact-types-get-by-id", methods=["GET"])
api.add_resource(ContactType, '/api/contact-types/update/<int:id>',endpoint="api-contact-types-put", methods=["PUT"])
api.add_resource(ContactType, '/api/contact-types/delete/<int:id>',endpoint="api-contact-types-delete", methods=["DELETE"])
api.add_resource(ContactTypeListSearch, '/api/contact-types/get',endpoint="api-contact-types-get-all", methods=["GET"])