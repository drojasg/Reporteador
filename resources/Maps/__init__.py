from config import api
from .Maps import Maps

#urls apis basicas
api.add_resource(Maps, '/api/maps/get-map',endpoint="api-maps-get-map", methods=["GET"])