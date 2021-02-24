from config import api
from .restriction import Restriction, getSpecificRestriction, OperaRestriction, OperaRestrictionCloseDate

#urls apis basicas
api.add_resource(Restriction, '/api/restriction/get',endpoint="api-restriction-get-all", methods=["GET"])
api.add_resource(Restriction, '/api/restriction/create',endpoint="api-restriction-post", methods=["POST"])
api.add_resource(Restriction, '/api/restriction/put/<int:id>',endpoint="api-restriction-put", methods=["PUT"])
api.add_resource(getSpecificRestriction, '/api/restriction/test',endpoint="api-restriction-test-all", methods=["GET"])
api.add_resource(OperaRestriction, '/api/restriction/create_opera',endpoint="api-restriction-opera-post", methods=["POST"])
api.add_resource(OperaRestrictionCloseDate, '/api/restriction/opera-close-dates',endpoint="api-restriction-opera-close-dates-get", methods=["POST"])
