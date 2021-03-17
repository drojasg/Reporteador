from config import api 
from.prueba import PruebaSearch, PruebaBookingSchema

api.add_resource(PruebaSearch, '/api/prueba/search/',endpoint="api-prueba-get", methods=["GET"])