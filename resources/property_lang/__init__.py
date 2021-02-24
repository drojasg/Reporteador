from config import api
from .property_lang import Propertylang, PropertylangSearch, PropertyLangList

#urls apis basicas
api.add_resource(Propertylang, '/api/property-lang/create',endpoint="api-property-lang-post", methods=["POST"])
api.add_resource(Propertylang, '/api/property-lang/search/<int:id>',endpoint="api-property-lang-get-by-id", methods=["GET"])
api.add_resource(Propertylang, '/api/property-lang/update/<int:id>',endpoint="api-property-lang-put", methods=["PUT"])
api.add_resource(Propertylang, '/api/property-lang/delete/<int:id>',endpoint="api-property-lang-delete", methods=["DELETE"])
api.add_resource(PropertylangSearch, '/api/property-lang/get',endpoint="api-property-lang-get-all", methods=["GET"])
api.add_resource(PropertyLangList, '/api/property-lang/search/property/<int:id>/<int:description_type>',endpoint="api-property-lang-get-property", methods=["GET"])