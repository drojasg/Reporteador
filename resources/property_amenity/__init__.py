from config import api
from .property_amenity import PropertyAmenity, PropertyAmenityListSearch, PublicPropertyAmenityList, PropertyGroupAmenityList, PropertyAmenityDescriptions

#urls apis basicas
#Administrativas
api.add_resource(PropertyAmenity, '/api/property-amenity/create',endpoint="api-property-amenity-post", methods=["POST"])
api.add_resource(PropertyAmenity, '/api/property-amenity/search/<int:id>',endpoint="api-property-amenity-get-by-id", methods=["GET"])
api.add_resource(PropertyAmenity, '/api/property-amenity/update/<int:id>',endpoint="api-property-amenity-put", methods=["PUT"])
api.add_resource(PropertyAmenity, '/api/property-amenity/delete/<int:id>',endpoint="api-property-amenity-delete", methods=["DELETE"])
api.add_resource(PropertyAmenityListSearch, '/api/property-amenity/get',endpoint="api-property-amenity-get-all", methods=["GET"])
api.add_resource(PropertyAmenityListSearch, '/api/property-amenity/update/property/<int:property>/<int:group>', endpoint='api-property-amenity-put-list', methods=["PUT"])
api.add_resource(PropertyAmenityDescriptions, '/api/property-amenity/get/property-amenity-descriptions/<int:iddef_property>/<string:lang_code>', endpoint='api-property-amenity-get-description', methods=["GET"])

#Publicas
api.add_resource(PublicPropertyAmenityList, '/api/public/property-amenity/search/property/<int:id>',endpoint="api-public-property-amenity-get-by-property", methods=["GET"])
api.add_resource(PropertyGroupAmenityList, '/api/property-amenity/search/<int:id>/<int:group>/<int:type>',endpoint="api-property-amenity-get-by-params", methods=["GET"])