from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import datetime
from config import db, base

from models.payment_method import PaymentMethod as Model, PaymentMethodSchema as ModelSchema
from common.util import Util

class PaymentMethod(Resource):

    # @base.access_middleware
    def get(self, id):
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

    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            
            if isinstance(json_data["config"], str):
                json_data["config"] = json.loads(request.json["tags"])
            else:
                json_data["config"] = json_data["config"]
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model.name = data["name"]
            model.description = data["description"]
            model.has_config = data["has_config"]
            model.config = data["config"]
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
            db.session.rollback()
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

    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.json
            
            if isinstance(json_data["config"], str):
                json_data["config"] = json.loads(request.json["config"])
            else:
                json_data["config"] = json_data["config"]
                
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
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
                
            if request.json.get("name") != None:
                model.name = data["name"]
            if request.json.get("description") != None:
                model.description = data["description"]
            if request.json.get("has_config") != None:
                model.has_config = data["has_config"]
            if request.json.get("config") != None:
                model.config = data["config"]
            model.estado = data["estado"]
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


class PaymentMethodList(Resource):

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
