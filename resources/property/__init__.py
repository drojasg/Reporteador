from config import api
from .property import Property, PropertyListSearch, PropertySearch, \
PropertyPublic, PropertyPublicListSearch, \
PropertyPublicSearchRooms, PublicPropertyListSearch, PropertyPublicHoldExp, \
PublicPropertyListSearchInfo, PropertyPublicAmenityMedia

#urls apis basicas
#Administrativas
api.add_resource(Property, '/api/property/create',endpoint="api-property-post", methods=["POST"])
api.add_resource(Property, '/api/property/search/<int:id>',endpoint="api-property-get-by-id", methods=["GET"])
api.add_resource(Property, '/api/property/update/<int:id>',endpoint="api-property-put", methods=["PUT"])
api.add_resource(Property, '/api/property/delete/<int:id>',endpoint="api-property-delete", methods=["DELETE"])
api.add_resource(PropertyListSearch, '/api/property/get',endpoint="api-property-get-all", methods=["GET"])
api.add_resource(PropertySearch, '/api/property-plans/get',endpoint="api-property-plans-get-all", methods=["GET"])

#Apis publicas
api.add_resource(PropertyPublic, '/api/public/property/search/<int:id>', endpoint='api-public-property-get-by-id', methods=["GET"])
api.add_resource(PropertyPublicListSearch, '/api/public/property/get', endpoint='api-public-property-get-all', methods=["POST"])
api.add_resource(PublicPropertyListSearch, '/api/v2/public/property/get', endpoint='api-public-property-get-all-v2', methods=["POST"])
#api.add_resource(PropertyPublicSearchHotels, '/api/public/search-hotels/get', endpoint='api-public-property-search-hotels-get', methods=["POST"])
api.add_resource(PropertyPublicSearchRooms, '/api/public/search-rooms/get', endpoint='api-public-property-search-rooms-get', methods=["POST"])
api.add_resource(PropertyPublicHoldExp, '/api/public/hold/get', endpoint='api-public-hold-expired-get', methods=["POST"])
api.add_resource(PublicPropertyListSearchInfo, '/api/v2/public/property-info/get', endpoint='api-public-property-info-get-all-v2', methods=["POST"])
api.add_resource(PropertyPublicAmenityMedia, '/api/v2/public/property-amenities/get', endpoint='api-public-property-amenities-get-v2', methods=["POST"])