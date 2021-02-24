from config import api
from .contact_info import ContactInfo, ContactInfoListSearch

api.add_resource(ContactInfo, '/api/public/contact/create',endpoint="api-public-contact-post", methods=["POST"])
api.add_resource(ContactInfo, '/api/public/contact/search/<int:id>', endpoint="api-public-contact-get-by-id", methods=["GET"])
api.add_resource(ContactInfoListSearch, '/api/public/contact/get',endpoint="api-public-contact-get", methods=["GET"])
#api.add_resource(ContactInfo, '/api/public/contact/update/<int:id>',endpoint="api-public-contact-put", methods=["PUT"])
#api.add_resource(ContactInfo, '/api/public/contact/delete/<int:id>',endpoint="api-public-contact-delete", methods=["DELETE"])
