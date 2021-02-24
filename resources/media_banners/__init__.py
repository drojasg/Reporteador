from config import api
from .media_banners import MediaBanners, MediaBannersList, BannersPublic, BannersTrade

api.add_resource(MediaBanners, '/api/media-banners/get/<int:id>', endpoint="api-media-banners-get-by-id", methods=["GET"])
api.add_resource(MediaBanners, '/api/media-banners/create', endpoint="api-media-banners-create", methods=["POST"])
api.add_resource(MediaBanners, '/api/media-banners/update', endpoint="api-media-banners-update", methods=["PUT"])
api.add_resource(MediaBannersList, '/api/media-banners/get', endpoint="api-media-banners-get-all", methods=["GET"])
api.add_resource(MediaBannersList, '/api/media-banners/update-status/<int:id>/<int:status>', endpoint="api-media-banners-update-status", methods=["PUT"])
api.add_resource(BannersTrade, '/api/media-banners/trade/get/<string:property_code>/<string:lang_code>/<string:market_code>/<string:booking_window>', endpoint="api-media-banners-trade-get", methods=["GET"])
api.add_resource(BannersPublic, '/api/public/media-banners/get/<string:property_code>/<string:brand_code>/<string:lang_code>/<string:market_code>/<string:booking_window>', endpoint="api-public-media-banners-get", methods=["GET"])