from config import api
from .address import AddressListSearch, Address

#urls apis basicas
api.add_resource(Address, '/api/addresses/create',endpoint="api-addresses-post", methods=["POST"])
api.add_resource(Address, '/api/addresses/search/<int:id>',endpoint="api-addresses-get-by-id", methods=["GET"])
api.add_resource(Address, '/api/addresses/update/<int:id>',endpoint="api-addresses-put", methods=["PUT"])
api.add_resource(Address, '/api/addresses/delete/<int:id>',endpoint="api-addresses-delete", methods=["DELETE"])
api.add_resource(AddressListSearch, '/api/addresses/get',endpoint="api-addresses-get-all", methods=["GET"])