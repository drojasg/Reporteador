from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
import secrets

from config import db, base
from common.util import Util
from sqlalchemy import and_, or_
from sqlalchemy.sql import exists
from models.credentials import Credentials as Model, CredentialsSchema as ModelSchema, AddCredentialsSchema, AddCredentialsChanelNameSchema
from models.channel import Channel,  ChannelSchema as channelSchema

class GetCredentials(Resource):
    #api-credentials-get-secret-token
    # @base.access_middleware
    def get(self):
        try:
            secret_token = self.get_credentials()
            response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": secret_token
                }

        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response
        
    @staticmethod
    def get_credentials():
        secret_token = secrets.token_urlsafe(16)
        data = db.session.query(exists().where(Model.api_key == secret_token)).scalar()
        
        #mientras exista seguirá buscando un nuevo token
        while data:
            secret_token = secrets.token_urlsafe(16)
            data = db.session.query(exists().where(Model.api_key == secret_token)).scalar()
        else:
            #si ya no existe retorna el nuevo token
            return secret_token

class Credentials(Resource):

    @staticmethod
    def exist_name(parameter):

        data = db.session.query(exists().where(Model.name == parameter)).scalar()

        if data:
            #si ya existe el nombre del parametro regresamos True
            return True
        else:
            #si no existe entonces False
            return False

    #api-credentials-add
    # @base.access_middleware
    def post(self):
        response = {}

        try:
            data= request.get_json(force=True)
            schema = AddCredentialsSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            model = Model()
        
            param_exist = self.exist_name(data["name"])

            if param_exist:
                raise Exception("The name" + " " + data["name"] + " " + "already exists, please enter a different name")
            else:
                model.name = data["name"]
                model.description = data["description"]
                model.api_key = data["api_key"]
                model.iddef_channel = data["iddef_channel"]
                model.restricted_ip = data["restricted_ip"]
                model.ip_list_allowed = data["ip_list_allowed"]
                model.restricted_dns = data["restricted_dns"]
                model.dns_list_allowed = data["dns_list_allowed"]
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
        #else:
            #response = {
                #"Code":500,
                #"Msg":"INVALID REQUEST"
            #}

        return response            

    #api-credentials-update
    # @base.access_middleware
    def put(self, id):
        try:
            data = request.get_json(force=True)
            schema = AddCredentialsSchema(exclude=Util.get_default_excludes())
            data = schema.load(data)
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            dataUpdate = model.query.filter_by(iddef_credentials=id).first()

            dataUpdate.name = data["name"]
            dataUpdate.description = data["description"]
            dataUpdate.iddef_channel = data["iddef_channel"]
            dataUpdate.restricted_ip = data["restricted_ip"]
            dataUpdate.ip_list_allowed = data["ip_list_allowed"]
            dataUpdate.restricted_dns = data["restricted_dns"]
            dataUpdate.dns_list_allowed = data["dns_list_allowed"]
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

    #api-credentials-search-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:

            data =Model.query.\
                join(Channel, Channel.iddef_channel == Model.iddef_channel)\
                .add_columns(Model.restricted_dns,Model.description,Model.restricted_ip,Model.ip_list_allowed,\
                Model.api_key,Model.name,Model.iddef_credentials,Model.iddef_channel,Model.dns_list_allowed,Model.estado,\
                (Channel.name).label("channel_name")).filter(Model.iddef_credentials == id).first()

            
            schema = AddCredentialsChanelNameSchema(exclude=Util.get_default_excludes())

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


class GetCredentialsList(Resource):
    #api-credentials-search-all
    # @base.access_middleware
    def get(self):
        try:
            data = Model.query.\
                join(Channel, Channel.iddef_channel == Model.iddef_channel)\
                .add_columns(Model.restricted_dns,Model.description,Model.restricted_ip,Model.ip_list_allowed,\
                Model.api_key,Model.name,Model.iddef_credentials,Model.iddef_channel,Model.dns_list_allowed,Model.estado,\
                (Channel.name).label("channel_name")).all()

            schema = AddCredentialsChanelNameSchema(exclude=Util.get_default_excludes(), many=True)
            if data is None:
                response = {
                    "code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response={
                    "code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data":schema.dump(data),
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response


class UpdateStatus(Resource):
    #api-credentials-update-status
    # @base.access_middleware
    def put(self, id):
        response = {}
        user_data = base.get_token_data()
        user_name = user_data
        try:
            json_data = request.get_json(force=True)
            schema = AddCredentialsSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)
            
                        
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = data["estado"]
            model.usuario_ultima_modificacion = "user_name"

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
