from config import api
from .promo_code import PromoCode, PromoCodeListSearch, PromoCodeListByVoucher

api.add_resource(PromoCode, '/api/promocode/search-id/<int:id>',endpoint="api-promocode-get-by-id", methods=["GET"])
api.add_resource(PromoCodeListSearch, '/api/promocode/search-all/get',endpoint="api-promocode-get-all", methods=["GET"])
api.add_resource(PromoCodeListByVoucher, '/api/promocode/search-by-voucher/<int:idVoucher>',endpoint="api-promocode-get-all-by-voucher", methods=["GET"])
api.add_resource(PromoCodeListByVoucher, '/api/promocode/create', endpoint="api-promocode-create-all", methods=["POST"])
api.add_resource(PromoCodeListByVoucher, '/api/promocode/update/<int:id>', endpoint="api-promocode-update-all", methods=["PUT"])
#api.add_resource(PromoCodeListByVoucher, '/api/promocode/delete/<int:id>', endpoint="api-promocode-delete-by-id", methods=["DELETE"])

