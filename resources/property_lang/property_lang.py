from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.property_lang import PropertyLangSchema as ModelSchema, GetPropertyLangSchema as GetModelSchema, PropertyLang as Model, GetDumpPropertyLangSchema
from common.util import Util
from sqlalchemy import or_, and_
from models.property_description import PropertyDescription, DumpPropertyDescriptionSchema

class Propertylang(Resource):
    #api-property-lang-get-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:

            data = Model.query.get(id)

            schema = GetModelSchema(exclude=Util.get_default_excludes())

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

    #api-property-lang-post
    # @base.access_middleware
    def post(self):
        
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                schema.load(data)
                model = Model()
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                
                #model.iddef_currency = data["iddef_property_lang"]
                model.iddef_property = data["iddef_property"]
                model.lang_code = data["lang_code"]
                #model.estado = data["estado"]
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
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST"
            }

        return response

    #api-property-lang-put
    # @base.access_middleware
    def put(self,id):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                model = Model()
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                dataUpdate = model.query.filter_by(iddef_property_lang=id).first()

                dataUpdate.iddef_property = data["iddef_property"]
                dataUpdate.lang_code = data["lang_code"]
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
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response

    #api-property-lang-delete
    # @base.access_middleware
    def delete(self,id):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                model = Model()
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                dataUpdate = model.query.filter_by(iddef_property_lang=id).first()

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
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response

class PropertyLangList(Resource):
    #api-property-lang-get-property
    # @base.access_middleware
    def get(self,id, description_type):

        response = {}

        try:

            data = Model.query.filter_by(iddef_property=id,estado=1).all()

            schema = GetDumpPropertyLangSchema(exclude=Util.get_default_excludes())
            result = schema.dump(data, many=True)

            schema_property_description = DumpPropertyDescriptionSchema(exclude=Util.get_default_excludes())
            for element in result:
                data_property_description = PropertyDescription.query.filter_by(iddef_property=id,lang_code=element["language_code"],iddef_description_type=description_type,estado=1).all()
                element.pop("iddef_property")
                element["descriptions"] = schema_property_description.dump(data_property_description, many=True)
            

            response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": result
                }

        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response

class PropertylangSearch(Resource):
    #api-property-lang-get-all
    # @base.access_middleware
    def get(self):
        try:

            schema = GetModelSchema(exclude=Util.get_default_excludes(), many=True)
            
            data = Model()
            
            value = request.args.get("all")
            propertyCode = request.args.get("property")

            conditions = []

            conditions.append(Model.estado==1)

            if value is not None:
                conditions.pop()
                

            if propertyCode is not None:
                val=int(propertyCode)
                conditions.append(Model.iddef_property==val)

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions)).all()
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