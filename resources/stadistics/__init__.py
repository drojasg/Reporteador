from config import api
from .stadistics import graphs

api.add_resource(graphs, '/api/stadistics/rate-on-lead-graph',endpoint="api-stadistics-rate-on-lead", methods=["POST"])