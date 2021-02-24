from config import api
from .book_hotel_room import BookHotelRoom

api.add_resource(BookHotelRoom, '/api/book-hotel-room/update-no-show', endpoint="api-book-hotel-room-update-no-show", methods=["PUT"])