from config import api
from .contact import ContactListSearch, Contact, ContactForm

#urls apis basicas
api.add_resource(Contact, '/api/contacts/create',endpoint="api-contacts-post", methods=["POST"])
api.add_resource(Contact, '/api/contacts/search/<int:id>',endpoint="api-contacts-get-by-id", methods=["GET"])
api.add_resource(Contact, '/api/contacts/update/<int:id>',endpoint="api-contacts-put", methods=["PUT"])
api.add_resource(Contact, '/api/contacts/delete/<int:id>',endpoint="api-contacts-delete", methods=["DELETE"])
api.add_resource(ContactListSearch, '/api/contacts/get',endpoint="api-contacts-get-all", methods=["GET"])

api.add_resource(ContactForm, '/api/contact-form/search/<int:id>/<int:iddef_contact_type>',endpoint="api-contacts-get-form", methods=["GET"])
api.add_resource(ContactForm, '/api/contact-form/create',endpoint="api-contacts-post-form", methods=["POST"])
api.add_resource(ContactForm, '/api/contact-form/update/<int:id>',endpoint="api-contacts-put-form", methods=["PUT"])