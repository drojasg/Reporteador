from config import api 
from.prueba import PruebaSearch

api.add_resource(PruebaSearch, '/api/prueba/search/<int:estado>',endpoint="api-prueba-get-by-estado", methods=["GET"])