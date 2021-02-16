from config import api
from .area_unit import AreaUnitListSearch, AreaUnit
from .book_address import BookAddressListSearch, BookAddress
from .def_property import DefPropertyListSearch, DefProperty

#urls apis basicas
api.add_resource(AreaUnit, '/api/area-unit/create',endpoint="api-area-unit-post", methods=["POST"])
#api.add_resource(AreaUnit, '/api/area-unit/search/<int:id>',endpoint="api-area-unit-get-by-id", methods=["GET"])
api.add_resource(AreaUnit, '/api/area-unit/update/<int:id>',endpoint="api-area-unit-put", methods=["PUT"])
api.add_resource(AreaUnit, '/api/area-unit/delete/<int:id>',endpoint="api-area-unit-delete", methods=["DELETE"])
api.add_resource(AreaUnitListSearch, '/api/area-unit/get',endpoint="api-area-unit-get-all", methods=["GET"])

api.add_resource(AreaUnit, '/api/pms/get/<int:id>',endpoint="api-area-unit-get-by-id", methods=["GET"])

#Booking_address
api.add_resource(BookAddress, '/api/address/search/<int:id>',endpoint="api-book-address-get-by-id", methods=["GET"])
api.add_resource(BookAddressListSearch, '/api/address/get',endpoint="api-area-address-get-all", methods=["GET"])

#def_property
api.add_resource(DefProperty, '/api/property/search/<int:id>',endpoint="api-def-property-get-by-id", methods=["GET"])
api.add_resource(DefPropertyListSearch, '/api/property/get',endpoint="api-def-property-get-all", methods=["GET"])

