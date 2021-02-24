from flask import Flask, request
from flask_restful import Resource
from sqlalchemy.sql import exists
from sqlalchemy import and_, or_
from config import db,base
from marshmallow import ValidationError
from models.auth_assignment import AuthAssignment as Model, AuthAssignmentSchema
from common.util import Util

class AuthAssignment(Resource):
    #api-auth-assignment-get
    #@base.access_middleware
    def get(self, item_name, credentials_id):
        try:
            schema = AuthAssignmentSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter(Model.item_name == item_name, Model.credentials_id == credentials_id, \
                Model.estado == 1).first()
            
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

    #api-auth-assignment-post
    #@base.access_middleware
    def post(self):
        
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthAssignmentSchema(exclude=Util.get_default_excludes())
            schema.load(data)            
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            exists_assign = db.session.query(
                exists().where(Model.item_name == data["item_name"])
                        .where(Model.credentials_id == data["credentials_id"])
            ).scalar()

            if exists_assign:
                raise Exception("The assignment exists")
            
            model.item_name = data["item_name"]
            model.credentials_id = data["credentials_id"]
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

    #api-auth-assignment-update-status
    #@base.access_middleware
    def put(self, item_name, credentials_id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = AuthAssignmentSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model.query.filter(Model.item_name == item_name, Model.credentials_id == credentials_id).first()
            
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = data["estado"]
            model.usuario_creacion = user_name

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
    
class AuthAssignmentSearch(Resource):
    #api-auth-assignment-get-all
    #@base.access_middleware
    def get(self, credentials_id):
        try:
            schema = AuthAssignmentSchema(exclude=Util.get_default_excludes(), many=True)
            data = Model.query.filter(Model.credentials_id == credentials_id).all()

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
    