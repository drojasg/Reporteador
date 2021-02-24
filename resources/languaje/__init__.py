from config import api
from .languaje import Language,LenguageListSearch, LenguageList, LenguageLangList

#urls apis basicas
api.add_resource(Language, '/api/language/create',endpoint="api-language-post", methods=["POST"])
api.add_resource(Language, '/api/language/search/<int:id>',endpoint="api-language-get-by-id", methods=["GET"])
api.add_resource(Language, '/api/language/update/<int:id>',endpoint="api-language-put", methods=["PUT"])
api.add_resource(Language, '/api/language/delete/<int:id>',endpoint="api-language-delete", methods=["DELETE"])
api.add_resource(LenguageListSearch, '/api/language/get',endpoint="api-language-get-all", methods=["GET"])
#public
api.add_resource(LenguageList, '/api/public/language/get',endpoint="api-public-language-get-all", methods=["GET"])
api.add_resource(LenguageLangList, '/api/public/language/get/<string:lang_code>',endpoint="api-public-language-lang-get-all", methods=["GET"])