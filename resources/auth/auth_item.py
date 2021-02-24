from flask import Flask, request
from flask_restful import Resource
from sqlalchemy.sql import exists
from sqlalchemy import and_, or_
from config import db, base
from marshmallow import ValidationError
from models.auth_item import AuthItem as Model, AuthItemSchema
from common.util import Util

class AuthItem(Resource):
    #api-auth-item-get
    #@base.access_middleware
    def get(self, name):
        try:
            schema = AuthItemSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(name)

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

    #api-auth-item-post
    #@base.access_middleware
    def post(self):
        
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthItemSchema(exclude=Util.get_default_excludes())
            schema.load(data)            
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            exists_name = db.session.query(exists().where(Model.name == data["name"])).scalar()

            if exists_name:
                raise Exception("The item {} exists".format(data["name"]))
            
            model.name = data["name"]
            model.type = data["type"]
            model.description = data["description"]
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
    
    #api-auth-item-put
    #@base.access_middleware
    def put(self, name):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthItemSchema(exclude=Util.get_default_excludes())
            schema.load(data)      
            model = Model.query.get(name)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if not model:
                raise Exception("Not Found")

            model.type = data["type"]
            model.description = data["description"]
            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name

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
    
class AuthItemSearch(Resource):
    #api-auth-item-get-all
    #@base.access_middleware
    def get(self):
        try:
            schema = AuthItemSchema(exclude=Util.get_default_excludes(), many=True)
            data = Model.query.all()

            #
            dataResponse = {}
            dataR = []

            isActives = request.args.get("actives")
            type = request.args.get("type")
            conditions = []

            if isActives is not None:
                conditions.append(Model.estado == 1)

            if type is not None:
                conditions.append(Model.type == type)

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions))
            else:
                data = Model.query.all()

            for datas in data:
                
                dataResponse[datas.name] =  datas.description

            dataR.append(dataResponse)

               

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
                    "data": schema.dump(data) #dataR#schema.dump(data)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

class AuthItemSearchDropDown(Resource):
    #api-auth-item-get-all-dropdown
    #@base.access_middleware
    def get(self):
        try:
            schema = AuthItemSchema(exclude=Util.get_default_excludes(), many=True)
            data = Model.query.all()

            #
            dataResponse = {}
            dataR = []

            isActives = request.args.get("actives")
            type = request.args.get("type")
            conditions = []

            if isActives is not None:
                conditions.append(Model.estado == 1)

            if type is not None:
                conditions.append(Model.type == type)

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions))
            else:
                data = Model.query.all()

            for datas in data:
                
                dataResponse[datas.name] =  datas.description

            dataR.append(dataResponse)

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
                    "data": dataR
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response