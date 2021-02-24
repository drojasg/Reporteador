from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db
from models.contact_info import ContactInfo as Model, ContactInfoSchema as ModelSchema
from common.util import Util
from common.public_auth import PublicAuth

class ContactInfo(Resource):
    #api
    @PublicAuth.access_middleware
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

    #api-contact-info-post
    @PublicAuth.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            #get api-key data
            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            
            model = Model()

            model.name = data["name"]
            model.phone = data["phone"]
            model.email = data["email"]
            model.agree_terms_conditions = data["agree_terms_conditions"]
            model.iddef_contact_info_time = data["iddef_contact_info_time"]
            model.estado = 1
            model.usuario_creacion = username
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

    @PublicAuth.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            #get api-key data
            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            
            model = Model.query.get(id)
    
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            if request.json.get("name") != None:
                model.name = data["name"]
            if request.json.get("phone") != None:
                model.phone = data["phone"]
            if request.json.get("email") != None:
                model.email = data["email"]
            if request.json.get("agree_terms_conditions") != None:
                model.agree_terms_conditions = data["agree_terms_conditions"]
            if request.json.get("iddef_contact_info_time") != None:
                model.iddef_contact_info_time = data["iddef_contact_info_time"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            model.usuario_ultima_modificacion = username
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

    @PublicAuth.access_middleware
    def delete(self, id):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            #get api-key data
            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            
            model = Model.query.get(id)

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = 0
            model.usuario_ultima_modificacion = username
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


class ContactInfoListSearch(Resource):
    #api-contact-info-get
    @PublicAuth.access_middleware
    def get(self):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            data = Model.query.filter(Model.estado==1).all()
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