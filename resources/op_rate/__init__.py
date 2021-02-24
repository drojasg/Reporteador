from config import api
from .op_rate import OpRate

api.add_resource(OpRate, '/api/v2/internal/rates/create',endpoint="api-internal-rate-post", methods=["POST"])