from config import api
from .log_apis import LogApis

#Basic APIs
api.add_resource(LogApis, '/api/log-apis/search', endpoint="api-log-apis-search", methods=["POST"])