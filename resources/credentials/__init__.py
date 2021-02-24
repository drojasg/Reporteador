from config import api
from .credentials import GetCredentials,Credentials,GetCredentialsList, UpdateStatus

api.add_resource(GetCredentials, '/api/credentials/get-secret-token',endpoint="api-credentials-get-secret-token", methods=["GET"])
api.add_resource(Credentials, '/api/credentials/add',endpoint="api-credentials-add", methods=["POST"])
api.add_resource(Credentials, '/api/credentials/update/<int:id>',endpoint="api-credentials-update", methods=["PUT"])
api.add_resource(Credentials, '/api/credentials/search-by-id/<int:id>',endpoint="api-credentials-search-by-id", methods=["GET"])
api.add_resource(GetCredentialsList, '/api/credentials/search-all',endpoint="api-credentials-search-all", methods=["GET"])
api.add_resource(UpdateStatus, '/api/credentials/update-status/<int:id>',endpoint="api-credentials-update-status", methods=["PUT"])