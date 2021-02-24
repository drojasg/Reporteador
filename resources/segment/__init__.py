from config import api
from .segment import SegmentListSearch, Segment

#urls apis basicas
api.add_resource(Segment, '/api/segment/create',endpoint="api-segment-post", methods=["POST"])
api.add_resource(Segment, '/api/segment/search/<int:id>',endpoint="api-segment-get-by-id", methods=["GET"])
api.add_resource(Segment, '/api/segment/update/<int:id>',endpoint="api-segment-put", methods=["PUT"])
api.add_resource(Segment, '/api/segment/delete/<int:id>',endpoint="api-segment-delete", methods=["DELETE"])
api.add_resource(SegmentListSearch, '/api/segment/get',endpoint="api-segment-get-all", methods=["GET"])