from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError, EXCLUDE
from flask import Flask, jsonify

from config import db, base
from models.terms_and_conditions import TermsAndConditionsSchema as ModelSchema, TermsAndConditionsRefSchema as ModelRefSchema, TermsAndConditions as Model
from common.util import Util
from common.public_auth import PublicAuth
from .terms_and_conditions_service import TermsAndConditionsService

class TermsAndConditions(Resource):

    #Administrador
    #api-property-get-by-id
    # @base.access_middleware
    def get(self,id):
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

    #Administrador
    #api-property-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data, unknown=EXCLUDE)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            model = Model()

            model.link_es = data["link_es"]
            model.link_en = data["link_en"]
            model.iddef_brand = data["iddef_brand"]
            model.estado = "1"
            model.usuario_creacion = user_name

            existsTerms = Model.query.filter_by(iddef_terms_and_conditions = model.iddef_terms_and_conditions).first()

            if existsTerms:
                raise Exception("The Terms %s exists" % model.terms_and_conditions)

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
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }

        return response

    #Administrador
    #api-property-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data,unknown=EXCLUDE)
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


            model.link_es = data["link_es"]
            model.link_en = data["link_en"]
            model.iddef_brand = data["iddef_brand"]
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

class TermsAndConditionsListSearch(Resource):

    #Administrador
    #api-terms-and-conditions-get-isAll
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

class TermsAndConditionsList(Resource):

    #api-terms_and_conditions-get-by-params
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())

            #obtenemos los datos de la tabla terms_and_conditions
            TermsData = Model.query.filter_by(iddef_brand=id, estado=1)

            #Se construye el response
            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": schema.dump(TermsData, many=True)
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

class TermsAndConditionsPublic(Resource):
    @PublicAuth.access_middleware
    def get(self, property_code, lang_code):
        response = {
            "Code": 200,
            "Msg": "",
            "Error": False,
            "data": {}
        }

        try:
            terms_cond = TermsAndConditionsService.get_terms_and_conditions_by_property(property_code)

            if not terms_cond:
                raise Exception("data not found")

            if lang_code == "es":
                response["data"] = terms_cond.link_es
            else:
                response["data"] = terms_cond.link_en
        
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
    
class TermsAndConditionsBrandPublic(Resource):
    @PublicAuth.access_middleware
    def get(self, brand_code, lang_code):
        response = {
            "Code": 200,
            "Msg": "",
            "Error": False,
            "data": {}
        }

        try:
            terms_cond = TermsAndConditionsService.get_terms_and_conditions_by_brand(brand_code)
            
            if not terms_cond:
                raise Exception("data not found")

            if lang_code == "es":
                response["data"] = terms_cond.link_es
            else:
                response["data"] = terms_cond.link_en
        
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
    