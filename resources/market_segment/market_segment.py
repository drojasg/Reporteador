from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.market_segment import MarketSegment as Model, MarketSegmentSchema as ModelSchema
from common.util import Util

class MarketSegment(Resource):
    #api-market-get-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            
            response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": schema.dump(data)
                }

        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response

    #api-market-post
    # @base.access_middleware
    def post(self):
        
        response = {}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema.load(data)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            model = Model()
                            
            model.code=data["code"]
            model.currency_code = data["currency_code"]
            model.description = data["description"]
            model.pms_profile_id = data["pms_profile_id"]
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

        return response

    #api-market-put
    # @base.access_middleware
    def put(self,id):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(data)
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            dataUpdate = model.query.get(id)            
            dataUpdate.code=data["code"]
            dataUpdate.currency_code = data["currency_code"]
            dataUpdate.description = data["description"]
            dataUpdate.pms_profile_id = data["pms_profile_id"]
            dataUpdate.estado = data["estado"]
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

        return response

    #api-market-delete
    # @base.access_middleware
    def delete(self,id):
        response = {}

        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            dataUpdate = Model.query.get(id)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
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

        return response

class MarketSegmentSearch(Resource):
    #api-market-get-all
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
