from config import api
from .img_compress import ImgCompress

api.add_resource(ImgCompress, "/api/compressImg/booking_engine", endpoint="api-compress-post", methods=["POST"])
