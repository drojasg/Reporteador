from config import api
from .op_contact_customer import OpContactCustomer

#url api-public
api.add_resource(OpContactCustomer, '/api/public/contact-customer/create',endpoint="api-public-contact-customer-create", methods=["POST"])
