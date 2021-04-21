from config import api 
from .prueba import PruebaSearch
from .book_customer_hotel import BookHotelCustomerSearch

api.add_resource(PruebaSearch, '/api/test/search',endpoint="api-prueba-get", methods=["GET"])
api.add_resource(BookHotelCustomerSearch, '/api/test/search1/',endpoint="api-prueba1-get", methods=["POST"])