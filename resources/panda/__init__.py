from config import api
from .panda import Panda

api.add_resource(Panda, '/api/test/panda/<string:nombre_archivo>',endpoint="api-test-panda-create", methods=["GET"])
