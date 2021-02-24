from config import api
from .channel_type import ChannelTypeSearch, ChannelType

api.add_resource(ChannelTypeSearch, '/api/channel-type/get',endpoint="api-channel-type-get-all", methods=["GET"])

api.add_resource(ChannelType, '/api/channel-type/create',endpoint="api-channel-type-post", methods=["POST"])
api.add_resource(ChannelType, '/api/channel-type/search/<int:id>',endpoint="api-channel-type-get-by-id", methods=["GET"])
api.add_resource(ChannelType, '/api/channel-type/update/<int:id>',endpoint="api-channel-type-put", methods=["PUT"])
api.add_resource(ChannelType, '/api/channel-type/delete/<int:id>',endpoint="api-channel-type-delete", methods=["DELETE"])
api.add_resource(ChannelTypeSearch, '/api/channel-type/update-status/<int:id>',endpoint="api-channel-type-update-status", methods=["PUT"])