from config import api 
from .prueba import PruebaSearch

api.add_resource(PruebaSearch, '/api/test/search',endpoint="api-prueba-get", methods=["GET"])