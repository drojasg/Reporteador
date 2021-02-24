from config import api
from .index import Index

api.add_resource(Index, "/")
