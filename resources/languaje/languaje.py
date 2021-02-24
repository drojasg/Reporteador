from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.languaje import GetLanguajeSchema as GetModelSchema, LanguajeSchema as ModelSchema, Languaje as Model
from models.text_lang import TextLang
from common.util import Util
from sqlalchemy.sql.expression import and_
from common.public_auth import PublicAuth

class Language(Resource):
    
    #api-language-get-by-id
    # @base.access_middleware
    def get(self,id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-language-post
    # @base.access_middleware
    def post(self):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                schema.load(data)
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                model = Model()
                
                #model.iddef_language = data["iddef_language"]
                model.lang_code = data["lang_code"]
                model.description = data["description"]
                #model.estado = data["estado"]
                model.usuario_creacion = user_name
                
                db.session.add(model)
                db.session.commit()
                    

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(model)
                }

            except ValidationError as Error:
                db.session.rollback()
                response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
            except Exception as e:
                

                db.session.rollback()
                response = {
                    "Code":500,
                    "Msg":str(e),
                    "Error":True,
                    "data":{}
                }
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST"
            }

        return response

    #api-language-put
    # @base.access_middleware
    def put(self,id):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                model = Model()
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                dataUpdate = model.query.filter_by(iddef_language=id).first()

                
                dataUpdate.lang_code = data["lang_code"]
                dataUpdate.description = data["description"]
                dataUpdate.usuario_ultima_modificacion = user_name
                
                db.session.commit()

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataUpdate)
                }

            except ValidationError as Error:
                response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
            except Exception as e:
                

                response = {
                    "Code":500,
                    "Msg":str(e),
                    "Error":True,
                    "data":{}
                }
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response

    #api-language-delete
    # @base.access_middleware
    def delete(self,id):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                model = Model()

                dataUpdate = model.query.filter_by(iddef_language=id).first()

                                
                dataUpdate.estado = 0
                dataUpdate.usuario_ultima_modificacion = user_name
                
                db.session.commit()

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataUpdate)
                }

            except ValidationError as Error:
                response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
            except Exception as e:
                

                response = {
                    "Code":500,
                    "Msg":str(e),
                    "Error":True,
                    "data":{}
                }
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response


class LenguageListSearch(Resource):
    #api-language-get-all
    # @base.access_middleware
    def get(self):
        try:

            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class LenguageList(Resource):
    #api-public-language-get-all
    @PublicAuth.access_middleware
    def get(self):
        try:
            result = []
            schema = GetModelSchema(many=True)
            # result = [
            #     {
            #         "description": "English",
            #         "iddef_language": 1,
            #         "lang_code": "EN",
            #         "estado":1
            #     },
            #     {
            #         "description": "Spanish",
            #         "iddef_language": 2,
            #         "lang_code": "ES",
            #         "estado":1
            #     },
            #     {
            #         "description": "Portuguese",
            #         "iddef_language": 3,
            #         "lang_code": "PO",
            #         "estado":1
            #     }
            # ]
            result = Model.query.filter_by(estado=1)

            if result is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(result)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class LenguageLangList(Resource):
    #api-public-language-lang-get-all
    @PublicAuth.access_middleware
    def get(self, lang_code):
        try:
            result = []
            schema = GetModelSchema(many=True)
            #result = Model.query.filter_by(estado=1)

            result = Model.query\
            .join(TextLang, and_(TextLang.id_relation == Model.iddef_language, TextLang.table_name == "def_language"))\
            .add_columns(Model.iddef_language, Model.lang_code, (TextLang.text).label("description"), Model.estado)\
            .filter(Model.estado==1, TextLang.estado==1, TextLang.lang_code == lang_code, TextLang.attribute == 'description').all()

            if result is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(result)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response