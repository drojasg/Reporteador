from config import api
from .service_pricing_type import ServicePricingTypeListSearch, ServicePricingType

#urls apis basicas
api.add_resource(ServicePricingType, '/api/service-pricing-type/create',endpoint="api-service-pricing-type-post", methods=["POST"])
api.add_resource(ServicePricingType, '/api/service-pricing-type/search/<int:id>',endpoint="api-service-pricing-type-get-by-id", methods=["GET"])
api.add_resource(ServicePricingType, '/api/service-pricing-type/update/<int:id>',endpoint="api-service-pricing-type-put", methods=["PUT"])
api.add_resource(ServicePricingType, '/api/service-pricing-type/delete/<int:id>',endpoint="api-service-pricing-type-delete", methods=["DELETE"])
api.add_resource(ServicePricingTypeListSearch, '/api/service-pricing-type/get',endpoint="api-service-pricing-type-get-all", methods=["GET"])