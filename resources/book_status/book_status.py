from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, timedelta
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql import exists

from config import app, db, base
from models.book_status import BookStatus as Model, BookStatusSchema as ModelSchema
from common.util import Util

class BookStatus(Resource):
    #api-book-status-get-by-id
    #@base.access_middleware
    def get(self,id):
                
        response = {}

        try:

            data = Model.query.get(id)

            schema = ModelSchema(exclude=Util.get_default_excludes())

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

    #api-book-status-create
    #@base.access_middleware
    def post(self):

        response = {}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            data_compare = data["name"].strip()

            param_exist = self.get_param_if_exists(data_compare.lower())

            if param_exist:
               raise Exception("The name" + " " + data["name"] + " " + "already exists, please enter a different name")
            else:
                model.name = data_compare.lower()
                model.code = data["code"]
                model.description = data["description"]
                model.estado = data["estado"]
                model.usuario_creacion = user_name
                db.session.add(model)
                db.session.commit()

            response={
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
                "Error": True,
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

    #api-book-status-update
    #@base.access_middleware
    def put(self, id):

        response = {}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()
            data_compare = data["name"].strip()
            
            #param_exist = self.get_param_if_exists(data["param"].strip())
            id_param_exist = self.get_param_if_exists_by_parameter_idconfig(id,data_compare.lower())

            if id_param_exist:
                #si existe, es el mismo id con el mismo nombre lo actualizamos
                dataUpdate = model.query.filter_by(idbook_status = id).first()

                dataUpdate.name = data_compare.lower()
                dataUpdate.code = data["code"]
                dataUpdate.description = data["description"]
                dataUpdate.estado = data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.flush()
            else:

                # si no lo insertamos, pero primero preguntamos si el nombre ya existe en toda la tabla
                param_exist = self.get_param_if_exists(data_compare.lower())
                if param_exist:
                    raise Exception("The name" + " " + data["name"] + " " + "already exists, please enter a different name")
                else:
                    model.name =  data_compare.lower()
                    model.code = data["code"]
                    model.description = data["description"]
                    model.estado = data["estado"]
                    model.usuario_creacion = user_name
                    db.session.add(model)
                    db.session.flush()
            
            db.session.commit()

            response={
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
                "Error": True,
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


    @staticmethod
    def get_param_if_exists(parameter):

        data = db.session.query(exists().where(Model.name == parameter)).scalar()

        if data:
            #si ya existe el nombre del parametro regresamos True
            return True
        else:
            #si no existe entonces False
            return False
    
    @staticmethod
    def get_param_if_exists_by_parameter_idconfig(id,parameter):
        
        data = db.session.query(exists().where(Model.idbook_status == id).where(Model.name == parameter)).scalar()

        if data:
            #si existe
            return True
        else:
            return False

class BookStatusListSearch(Resource):
    #api-book-status-search-list
    #@base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.all()

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

    #api-book-status-delete-status
    #@base.access_middleware
    def put(self, id):
        #update Status
        response = {}
        try:
            json_data = request.get_json(force=True)
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

            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

            result = schema.dump(model)
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
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