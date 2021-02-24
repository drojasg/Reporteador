from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_tax_group import PolicyTaxGroupSchema as ModelSchema, PolicyTaxGroup as Model, GetPolicyTaxGroupSchema as GetModelSchema
from common.util import Util


class PolicyTaxGroup(Resource):
    #api-policy_tax_groups-get-by-id
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

    #api-policy_tax_groups-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetModelSchema(exclude=Util.get_default_excludes())
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
            if request.json.get("iddef_policy_tax_base") != None:
                model.iddef_policy_tax_base = data["iddef_policy_tax_base"]
            if request.json.get("iddef_policy_tax_type") != None:
                model.iddef_policy_tax_type = data["iddef_policy_tax_type"]
            if request.json.get("iddef_policy_tax_price") != None:
                model.iddef_policy_tax_price = data["iddef_policy_tax_price"]
            if request.json.get("iddef_policy_tax_vat") != None:
                model.iddef_policy_tax_vat = data["iddef_policy_tax_vat"]
            if request.json.get("amount") != None:
                model.amount = data["amount"]
            if request.json.get("max_amount") != None:
                model.max_amount = data["max_amount"]
            if request.json.get("is_custom_text") != None:
                model.is_custom_text = data["is_custom_text"]
            if request.json.get("description_en") != None:
                model.description_en = data["description_en"]
            if request.json.get("description_es") != None:
                model.description_es = data["description_es"]
            if request.json.get("use_maximum_amount") != None:
                model.use_maximum_amount = data["use_maximum_amount"]
            if request.json.get("use_custom_desc") != None:
                model.use_custom_desc = data["use_custom_desc"]
            if request.json.get("use_ages_range") != None:
                model.use_ages_range = data["use_ages_range"]
            if request.json.get("age_ranges") != None:
                model.age_ranges = data["age_ranges"]
            if request.json.get("use_dates_range") != None:
                model.use_dates_range = data["use_dates_range"]
            if request.json.get("date_ranges") != None:
                model.date_ranges = data["date_ranges"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
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


class PolicyTaxGroupDelete(Resource):
    #api-policy_tax_groups-delete
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
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

            model.estado = 0
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


class PolicyTaxGroupListSearch(Resource):
    #api-policy_tax_groups-get-all
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

    #api-policy_tax_groups-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)           
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            #model.iddef_policy_tax_group = data["iddef_policy_tax_group"]
            model.iddef_policy = data["iddef_policy"]
            model.iddef_policy_tax_base = data["iddef_policy_tax_base"]
            model.iddef_policy_tax_type = data["iddef_policy_tax_type"]
            model.iddef_policy_tax_price = data["iddef_policy_tax_price"]
            model.iddef_policy_tax_vat = data["iddef_policy_tax_vat"]
            model.amount = data["amount"]
            model.max_amount = data["max_amount"]
            model.is_custom_text = data["is_custom_text"]
            model.description_en = data["description_en"]
            model.description_es = data["description_es"]
            model.use_maximum_amount = data["use_maximum_amount"]
            model.use_custom_desc = data["use_custom_desc"]
            model.use_ages_range = data["use_ages_range"]
            model.age_ranges = request.json.get("age_ranges", [])
            model.use_dates_range = data["use_dates_range"]
            model.date_ranges = request.json.get("date_ranges", [])
            model.estado = 1
            model.usuario_creacion = user_name
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

