from flask import Flask, request
from flask_restful import Resource
from sqlalchemy.sql import exists
from sqlalchemy import and_, or_
from config import db, base
from marshmallow import ValidationError
from models.auth_item_child import AuthItemChild as Model, AuthItemChildSchema
from common.util import Util

class AuthItemChild(Resource):
    #api-auth-child-get
    #@base.access_middleware
    def get(self, parent, child):
        try:
            schema = AuthItemChildSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter(Model.parent == parent, Model.child == child).first()
            
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

    #api-auth-child-post
    #@base.access_middleware
    def post(self):
        
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthItemChildSchema(exclude=Util.get_default_excludes())
            schema.load(data)            
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            exists_assign = db.session.query(
                exists().where(Model.parent == data["parent"])
                        .where(Model.child == data["child"])
            ).scalar()

            if exists_assign:
                raise Exception("The child {} exists in the parent {}".format(data["child"], data["parent"]))
            
            model.parent = data["parent"]
            model.child = data["child"]
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
    
    #api-auth-child-update
    #@base.access_middleware
    def put(self, parent, child):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthItemChildSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model.query.filter(Model.parent == parent, Model.child == child).first()
            
            if not model:
                raise Exception("Not Found")
            
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
    
class AuthItemChildSearch(Resource):
    #api-auth-child-get-all
    #@base.access_middleware
    def get(self, parent):
        try:
            schema = AuthItemChildSchema(exclude=Util.get_default_excludes(), many=True)
            data = Model.query.filter(Model.parent == parent, Model.estado == 1).all()

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
    