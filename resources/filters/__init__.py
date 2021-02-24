from config import api
from .filters import Filter, FilterListSearch

#urls apis basicas
api.add_resource(Filter, '/api/filters/create',endpoint="api-filters-post", methods=["POST"])
api.add_resource(Filter, '/api/filters/search/<int:id>',endpoint="api-filters-get-by-id", methods=["GET"])
api.add_resource(Filter, '/api/filters/update/<int:id>',endpoint="api-filters-put", methods=["PUT"])
api.add_resource(Filter, '/api/filters/delete/<int:id>',endpoint="api-filters-delete", methods=["DELETE"])
api.add_resource(FilterListSearch, '/api/filters/get',endpoint="api-filters-get-all", methods=["GET"])
api.add_resource(FilterListSearch, '/api/filters/update-status/<int:id>',endpoint="api-filters-update-status", methods=["PUT"])