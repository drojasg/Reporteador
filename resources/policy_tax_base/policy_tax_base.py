from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_tax_base import PolicyTaxBaseSchema as ModelSchema, PolicyTaxBase as Model, GetPolicyTaxBaseSchema as GetModelSchema
from common.util import Util


class PolicyTaxBase(Resource):
    #api-policy_tax_bases-get-by-id
    # @base.access_middleware
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

    # def put(self, id):
    #   response = {}
    #   try:
    #       json_data = request.get_json(force=True)
    #       schema = GetModelSchema(exclude=Util.get_default_excludes())
    #       data = schema.load(json_data)
    #       model = Model.query.get(id)

    #       user_data = base.get_token_data()
    #       user_name = user_data['user']['username']
    
    #       if model is None:
    #           return {
    #               "Code": 404,
    #               "Msg": "data not found",
    #               "Error": True,
    #               "data": {}
    #           }
    #       if request.json.get("iddef_policy_category") != None:
    #           model.iddef_policy_category = data["iddef_policy_category"]
    #       if request.json.get("is_default") != None:
    #           model.is_default = data["is_default"]
    #       if request.json.get("option_selected") != None:
    #           model.option_selected = data["option_selected"]
    #       if request.json.get("text_only_policy") != None:
    #           model.text_only_policy = data["text_only_policy"]
    #       if request.json.get("estado") != None:
    #           model.estado = data["estado"]
    #       model.usuario_ultima_modificacion = user_name
    #       db.session.commit()

    #       response = {
    #           "Code": 200,
    #           "Msg": "Success",
    #           "Error": False,
    #           "data": schema.dump(model)
    #       }
    #   except ValidationError as error:
    #       response = {
    #           "Code": 500,
    #           "Msg": error.messages,
    #           "Error": True,
    #           "data": {}
    #       }
    #   except Exception as e:
    #       db.session.rollback()
    #       response = {
    #           "Code": 500,
    #           "Msg": str(e),
    #           "Error": True,
    #           "data": {}
    #       }

    #   return response

    # def delete(self, id):
    #   response = {}
    #   try:
    #       schema = ModelSchema(exclude=Util.get_default_excludes())
    #       model = Model.query.get(id)

    #       user_data = base.get_token_data()
    #       user_name = user_data['user']['username']

    #       if model is None:
    #           return {
    #               "Code": 404,
    #               "Msg": "data not found",
    #               "Error": True,
    #               "data": {}
    #           }

    #       model.estado = 0
    #       model.usuario_ultima_modificacion = user_name
    #       db.session.commit()

    #       response = {
    #           "Code": 200,
    #           "Msg": "Success",
    #           "Error": False,
    #           "data": schema.dump(model)
    #       }
    #   except ValidationError as error:
    #       response = {
    #           "Code": 500,
    #           "Msg": error.messages,
    #           "Error": True,
    #           "data": {}
    #       }
    #   except Exception as e:
    #       db.session.rollback()
    #       response = {
    #           "Code": 500,
    #           "Msg": str(e),
    #           "Error": True,
    #           "data": {}
    #       }

    #   return response


class PolicyTaxBaseListSearch(Resource):
    #api-policy_tax_bases-get-all
    # @base.access_middleware
    def get(self):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
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

    # def post(self):
    #   response = {}
    #   try:
    #       json_data = request.get_json(force=True)
    #       schema = ModelSchema(exclude=Util.get_default_excludes())
    #       data = schema.load(json_data)           
    #       model = Model()

    #       user_data = base.get_token_data()
    #       user_name = user_data['user']['username']
            
    #       #model.iddef_policy = data["iddef_policy"]
    #       model.iddef_policy_category = data["iddef_policy_category"]
    #       model.is_default = data["is_default"]
    #       model.option_selected = data["option_selected"]
    #       model.text_only_policy = data["text_only_policy"]
    #       model.estado = 1
    #       model.usuario_creacion = user_name
    #       db.session.add(model)
    #       db.session.commit()

    #       response = {
    #           "Code": 200,
    #           "Msg": "Success",
    #           "Error": False,
    #           "data": schema.dump(model)
    #       }
    #   except ValidationError as error:
    #       db.session.rollback()
    #       response = {
    #           "Code": 500,
    #           "Msg": error.messages,
    #           "Error": True,
    #           "data" : {}
    #       }
    #   except Exception as e:
    #       db.session.rollback()
    #       response = {
    #           "Code": 500,
    #           "Msg": str(e),
    #           "Error": True,
    #           "data" : {}
    #       }
        
    #   return response

