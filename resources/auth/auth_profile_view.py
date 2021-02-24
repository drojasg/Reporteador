from flask import Flask, request
from flask_restful import Resource
from sqlalchemy.sql import exists
from sqlalchemy import and_, or_
from config import db, base
from marshmallow import ValidationError
from models.auth_profile_view import AuthProfileView as Model, AuthProfileViewSchema
from common.util import Util

class AuthProfileView(Resource):
    #api-auth-profile-view-get
    #@base.access_middleware
    def get(self, id):
        try:
            schema = AuthProfileViewSchema(exclude=Util.get_default_excludes())
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

    #api-auth-profile-view-post
    #@base.access_middleware
    def post(self):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthProfileViewSchema(exclude=Util.get_default_excludes())
            schema.load(data)            
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            exists_profile = db.session.query(
                exists().where(Model.auth_item == data["auth_item"])
                        .where(Model.controller == data["controller"])
                        .where(Model.action == data["action"])
            ).scalar()

            if exists_profile:
                raise Exception("The profile view exists: {} - {} - {}".format(data["auth_item"], data["controller"], data["action"]))
            
            model.auth_item = data["auth_item"]
            model.controller = data["controller"]
            model.action = data["action"]
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
    
    #api-auth-profile-view-update
    #@base.access_middleware
    def put(self, id):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthProfileViewSchema(exclude=Util.get_default_excludes())
            schema.load(data)      
            model = Model.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if not model:
                raise Exception("Not Found")

            exists_profile = db.session.query(
                exists().where(Model.auth_item == data["auth_item"])
                        .where(Model.controller == data["controller"])
                        .where(Model.action == data["action"])
                        .where(Model.id_profile_view != id)
            ).scalar()

            if exists_profile:
                raise Exception("The profile view exists: {} - {} - {}".format(data["auth_item"], data["controller"], data["action"]))

            model.auth_item = data["auth_item"]
            model.controller = data["controller"]
            model.action = data["action"]
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
    
class AuthProfileViewSearch(Resource):
    #api-auth-profile-view-get-all
    #@base.access_middleware
    def get(self):
        try:
            schema = AuthProfileViewSchema(exclude=Util.get_default_excludes(), many=True)

            isAll = request.args.get("all")
            auth_item = request.args.get("auth_item")
            controller = request.args.get("controller")
            conditions = []

            if isAll is None:
                conditions.append(Model.estado == 1)

            if auth_item is not None:
                conditions.append(Model.auth_item == auth_item)
            
            if controller is not None:
                conditions.append(Model.controller == controller)

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions))
            else:
                data = Model.query.all()

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


class AuthProfileViewRole(Resource):
    #api-auth-profile-view-post-role-by-endpoint
    #@base.access_middleware
    def post(self):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = AuthProfileViewSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
                      
                        
            for x in  data["action"]:
                model = Model()
               
                model.auth_item = data["auth_item"]
                model.controller = ""
                model.action = x
                model.estado = 1
                model.usuario_creacion = user_name
                
                db.session.add(model)
                db.session.flush()
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