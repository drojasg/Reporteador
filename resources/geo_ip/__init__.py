from config import api
from .geo_ip import GeoIp, GeoIpPublic, GeoCountryPublic

#urls apis basicas
api.add_resource(GeoIpPublic, '/api/public/geo-ip/<string:ip>',endpoint="api-public-get-by-ip", methods=["GET"])
api.add_resource(GeoCountryPublic, '/api/public/geo-country/<string:market_code>',endpoint="api-public-get-by-market_code", methods=["GET"])
api.add_resource(GeoIp, '/api/geo-ip/create',endpoint="api-geo-ip-post", methods=["POST"])