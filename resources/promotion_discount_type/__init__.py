from config import api
from .promotion_discount_type import PromotionDiscountTypeListSearch

#urls apis basicas
api.add_resource(PromotionDiscountTypeListSearch, '/api/promotion-discount-type/get',endpoint="api-promotion-discount-type-get-all", methods=["GET"])