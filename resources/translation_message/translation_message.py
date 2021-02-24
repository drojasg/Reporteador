from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db,base
from models.translation_message import TranslationMessageSchema as ModelSchema,  TranslationMessage as Model
from common.util import Util
from common.public_auth import PublicAuth
from sqlalchemy import or_, and_
class TranslationMessage(Resource):
    #api-translation-message-get-by-id
    @PublicAuth.access_middleware
    def get(self, lang, page):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            
            data = Model.query.filter_by(lang_code = lang, page = page, estado = 1).all()

            if len(data) ==0:
                data = Model.query.filter_by(lang_code = 'en', page = page, estado = 1).all()


            data_result = schema.dump(data)
            response = []

            aux={}

            
            for data in data_result:
                
                aux["{key}".format(key=data['key'])] = data['text']
                       
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
                    "data": aux
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    # @base.access_middleware
    def post(self):
        response = {}

        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #user_name = "Test"

            model = Model.query.filter(Model.lang_code==data["lang_code"],Model.key==data["key"],\
            Model.page ==data["page"]).first()

            if model is not None:
                raise Exception("Ya existe un registro igual al que se intenta ingresar")
                
            model = Model()
            
            model.lang_code = data["lang_code"]
            model.key = data["key"]
            model.text = data["text"]
            model.allow_public = data["allow_public"]
            model.page = data["page"]
            model.estado = data["estado"]
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }

        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as error_msg:
            response = {
                "Code": 500,
                "Msg": str(error_msg),
                "Error": True,
                "data": {}
            }

        return response

    # @base.access_middleware
    def put(self,id):
        response = {}

        try:


            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #user_name = "Test"

            model.lang_code = data["lang_code"]
            model.key = data["key"]
            model.text = data["text"]
            model.allow_public = data["allow_public"]
            model.page = data["page"]
            model.estado = data["estado"]
            model.usuario_creacion = user_name
            #db.session.add(model)
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }

        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as error_msg:
            response = {
                "Code": 500,
                "Msg": str(error_msg),
                "Error": True,
                "data": {}
            }

        return response
    
    #api-time-zone-put
    # @base.access_middleware
    def delete(self, id):
        response = {}
        try:
            #json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            #data = schema.load(json_data)
            model = Model.query.get(id)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            # if request.json.get("name") != None:
            #     model.name = data["name"]
            # if request.json.get("code") != None:
            #     model.code = data["code"]
            # if request.json.get("estado") != None:
            model.estado = 0
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class TranslationMessageV2(Resource):

    def get(self):
        try:
            data = Model.query.filter(Model.estado == 1, Model.page == "all", Model.allow_public == 1)
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            data_dump = schema.dump(data)

            data_en = {}
            data_es = {}
            
            for i in data_dump:
                if i['lang_code'] == "en":
                    data_en[i['key']] = i['text'] 
                else:
                    data_es[i['key']] = i['text']

            data_languajes = {'ES': data_es, 'EN':data_en}
            
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
                    "data": data_languajes
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response