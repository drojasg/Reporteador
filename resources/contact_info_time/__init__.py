from config import api
from .contact_info_time import ContactInfoTime, ContactInfoTimeListSearch

api.add_resource(ContactInfoTime, '/api/public/contact-time/create',endpoint="api-public-contact-time-post", methods=["POST"])
api.add_resource(ContactInfoTime, '/api/public/contact-time/search/<int:id>',endpoint="api-public-contact-time-search", methods=["GET"])
api.add_resource(ContactInfoTimeListSearch, '/api/public/contact-time/get',endpoint="api-public-contact-time-get", methods=["GET"])
#api.add_resource(ContactInfoTime, '/api/public/contact-time/update/<int:id>',endpoint="api-public-contact-time-put", methods=["PUT"])
#api.add_resource(ContactInfoTime, '/api/public/contact-time/delete/<int:id>',endpoint="api-public-contact-time-delete", methods=["DELETE"])
