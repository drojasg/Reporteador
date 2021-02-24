from config import api
from .book_status import BookStatus, BookStatusListSearch

api.add_resource(BookStatus, '/api/book_status/search/<int:id>',endpoint="api-book-status-get-by-id", methods=["GET"])
api.add_resource(BookStatus, '/api/book_status/create',endpoint="api-book-status-create", methods=["POST"])
api.add_resource(BookStatus, '/api/book_status/update/<int:id>',endpoint="api-book-status-update", methods=["PUT"])
api.add_resource(BookStatusListSearch, '/api/book-status/search-all',endpoint="api-book-status-search-list", methods=["GET"])
api.add_resource(BookStatusListSearch, '/api/config_booking/delete-status/<int:id>',endpoint="api-book-status-delete-status", methods=["PUT"])