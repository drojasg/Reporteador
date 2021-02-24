from config import api
from .translation_message import TranslationMessage, TranslationMessageV2

#URL API-Pública.
api.add_resource(TranslationMessage, '/api/public/text/<string:lang>/<string:page>',endpoint="api-public-text-get", methods=["GET"])
api.add_resource(TranslationMessage, '/api/text/create',endpoint="api-public-text-post", methods=["POST"])
api.add_resource(TranslationMessage, '/api/text/update/<int:id>',endpoint="api-public-text-put", methods=["PUT"])
api.add_resource(TranslationMessage, '/api/text/delete/<int:id>',endpoint="api-public-text-delete", methods=["DELETE"])

#API GET ver2 
api.add_resource(TranslationMessageV2, '/api/v2/public/text',endpoint="api-v2-public-text-get", methods=["GET"])