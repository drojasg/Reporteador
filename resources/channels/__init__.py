from config import api
from .channels import Channel, ChannelListSearch,channelsSearchTable

#urls apis basicas
#
#
#api.add_resource(Channel, '/api/currency/delete/<int:id>',endpoint="api-currency-delete", methods=["DELETE"])
api.add_resource(ChannelListSearch, '/api/channels/get-all',endpoint="api-channels-get-all", methods=["GET"])
api.add_resource(Channel, '/api/channels/search/<int:id>',endpoint="api-channels-get-by-id", methods=["GET"])
api.add_resource(Channel, '/api/channels/create',endpoint="api-channels-post", methods=["POST"])
api.add_resource(Channel, '/api/channels/update/<int:id>',endpoint="api-channels-put", methods=["PUT"])
api.add_resource(channelsSearchTable, '/api/channels/get-table', endpoint="api-channels-get-info-table", methods=['GET'])
api.add_resource(channelsSearchTable, '/api/channels/delete-status/<int:id>',endpoint="api-channels-delete-status", methods=["PUT"])
