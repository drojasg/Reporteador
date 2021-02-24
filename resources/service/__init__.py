from config import api
from .service import ServiceLangSearch, ServiceListSearch, Service, ServiceProperty, PublicServicePropertyLang, ServicePropertyAdditional

#urls apis basicas
api.add_resource(Service, '/api/service/create',endpoint="api-service-post", methods=["POST"])
api.add_resource(Service, '/api/service/search/<int:id>',endpoint="api-service-get-by-id", methods=["GET"])
#api.add_resource(Service, '/api/service/update/<int:id>',endpoint="api-service-put", methods=["PUT"])
api.add_resource(Service, '/api/service/delete/<int:id>/<int:estado>',endpoint="api-service-delete", methods=["PUT"])
api.add_resource(ServiceListSearch, '/api/service/get',endpoint="api-service-get-all", methods=["GET"])
api.add_resource(ServiceLangSearch, '/api/service/search-property-lang/<int:id>/<int:id_property>',endpoint="api-service-text-lang", methods=["GET"])
api.add_resource(ServiceProperty, '/api/service/search-property/<int:id_property>',endpoint="api-service-property", methods=["GET"])

#Apis publicas
api.add_resource(PublicServicePropertyLang, '/api/public/service/property-lang/<int:id_property>/<string:market>/<string:lang_code>',endpoint="api-public-service-lang", methods=["GET"])
api.add_resource(ServicePropertyAdditional, '/api/public/service-property/additional/get',endpoint="api-public-service-additional", methods=["POST"])