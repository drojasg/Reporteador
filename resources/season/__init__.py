from config import api
from .season import Season, SeasonList
# SeasonListSearch,

#urls apis basicas
#Administrativas
#api.add_resource(Season, '/api/season/search-id/<int:id>', endpoint="api-season-get-by-id", methods=["GET"])
#api.add_resource(Season, '/api/season/update/<int:idSeason>/<int:idPeriod>',endpoint="api-season-put", methods=["PUT"])
api.add_resource(SeasonList, '/api/season/create',endpoint="api-season-post", methods=["POST"])
api.add_resource(SeasonList, '/api/season/search/<int:idHotel>', endpoint="api-season-get-by-params", methods=["GET"])
api.add_resource(Season, '/api/season/update/<int:id>', endpoint="api-season-put", methods=["PUT"])
