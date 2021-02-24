from config import api
from .promotion_discount_format import PromotionDiscountFormatListSearch

#urls apis basicas
api.add_resource(PromotionDiscountFormatListSearch, '/api/promotion-discount-format/get',endpoint="api-promotion-discount-format-get-all", methods=["GET"])