from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.price_type import PriceTypeSchema as ModelSchema, GetPriceTypeSchema as GetModelSchema, PriceType as Model
from common.util import Util


class PriceType(Resource):
    #api-price-type-get-by-id
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

    #api-price-type-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.json
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model.query.get(id)

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
                
            model.decription = data["decription"]
            if request.json.get("estado") != None:
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

    #api-price-type-delete
    # @base.access_middleware
    def delete(self, id):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
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

    #api-price-type-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.json
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            model.decription = data["decription"]
            model.estado = 1
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

class PriceTypeListSearch(Resource):
    #api-price-type-get-all
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