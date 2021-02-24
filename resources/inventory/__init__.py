from config import api
from .inventory import InventoryListSearch, Inventory

#urls apis basicas
api.add_resource(Inventory, '/api/inventory/create',endpoint="api-inventory-post", methods=["POST"])
api.add_resource(Inventory, '/api/inventory/search/<int:id>',endpoint="api-inventory-get-by-id", methods=["GET"])
api.add_resource(Inventory, '/api/inventory/update/<int:id>',endpoint="api-inventory-put", methods=["PUT"])
#api.add_resource(Inventory, '/api/inventory/delete/<int:id>',endpoint="api-inventory-delete", methods=["DELETE"])
api.add_resource(InventoryListSearch, '/api/inventory/get',endpoint="api-inventory-get-all", methods=["GET"])