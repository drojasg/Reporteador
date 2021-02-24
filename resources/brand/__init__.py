from config import api
from .brand import BrandListSearch, Brand

#urls apis basicas
api.add_resource(Brand, '/api/brand/create',endpoint="api-brand-post", methods=["POST"])
api.add_resource(Brand, '/api/brand/search/<int:id>',endpoint="api-brand-get-by-id", methods=["GET"])
api.add_resource(Brand, '/api/brand/update/<int:id>',endpoint="api-brand-put", methods=["PUT"])
api.add_resource(Brand, '/api/brand/delete/<int:id>',endpoint="api-brand-delete", methods=["DELETE"])
api.add_resource(BrandListSearch, '/api/brand/get',endpoint="api-brand-get-all", methods=["GET"])
api.add_resource(BrandListSearch, '/api/brand/delete-status/<int:id>',endpoint="api-brand-delete-status", methods=["PUT"])