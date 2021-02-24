from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_payment_1 import PolicyPaymentSchema as ModelSchema, PolicyPaymentCreateUpdateSchema as PostPutSchema, PolicyPayment as Model, GetPolicyPaymentSchema
from models.policy import PolicySchema, Policy as PolicyModel
from models.market_segment import MarketSegment, MarketSegmentSchema
from models.country import Country, CountrySchema
from common.util import Util
from common.public_auth import PublicAuth
from sqlalchemy.sql.expression import and_,func
from io import StringIO
import json

class PolicyPayment(Resource):
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            dataJson = request.get_json(force=True)
            schema = PostPutSchema()
            #data = schema.load(dataJson)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []

            # Insertamos en la tabla de policy
            modelPolicy = PolicyModel()

            modelPolicy.policy_code = dataJson["policy_code"]
            modelPolicy.iddef_currency = 1
            modelPolicy.iddef_policy_category = 4
            modelPolicy.is_default = 0
            modelPolicy.option_selected = 0
            modelPolicy.text_only_policy = 0
            modelPolicy.available_dates = []
            modelPolicy.estado = 1
            modelPolicy.usuario_creacion = user_name

            db.session.add(modelPolicy)
            db.session.flush()

            PolicySchemaDump = PolicySchema(
                exclude=Util.get_default_excludes())

            insertPolicy = PolicySchemaDump.dump(modelPolicy)
            dataResponse.append(insertPolicy)

            # insertamos en la tabla de policy_payment
            modelPolicyPayment = Model()

            modelPolicyPayment.iddef_policy = insertPolicy['iddef_policy']

            ####################Campos nuevos###################################
            modelPolicyPayment.market_segment_list = dataJson["market_segment_list"]
            modelPolicyPayment.property_list = dataJson["property_list"]
            ####################################################################


            modelPolicyPayment.description_en = dataJson["description_en"]
            modelPolicyPayment.description_es = dataJson["description_es"]
            modelPolicyPayment.estado = 1
            modelPolicyPayment.usuario_creacion = user_name

            db.session.add(modelPolicyPayment)
            db.session.flush()

            PolicyPaymentDump = ModelSchema(
                exclude=Util.get_default_excludes())

            insertPolicyPayment = PolicyPaymentDump.dump(modelPolicyPayment)
            dataResponse.append(insertPolicyPayment)

            if insertPolicy and insertPolicyPayment:
                db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataResponse
            }

        except ValidationError as Error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": Error.messages,
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

    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            dataJson = request.get_json(force=True)
            schema = PostPutSchema()
            #data = schema.load(dataJson)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []

            # modificamos en la tabla de policy_payment
            modelPolicyPayment = Model()

            PolicyPaymentUpdate = modelPolicyPayment.query.filter_by(
                iddef_policy_payment=id).first()
            PolicyPaymentDump = ModelSchema(
                exclude=Util.get_default_excludes())

            policy_payment = PolicyPaymentDump.dump(PolicyPaymentUpdate)

            #
            PolicyPaymentUpdate.market_segment_list = dataJson["market_segment_list"]
            PolicyPaymentUpdate.property_list = dataJson["property_list"]
            #
            PolicyPaymentUpdate.description_en = dataJson["description_en"]
            PolicyPaymentUpdate.description_es = dataJson["description_es"]
            PolicyPaymentUpdate.estado = dataJson['estado']
            PolicyPaymentUpdate.usuario_creacion = user_name
            db.session.flush()

            UpdatePayment = PolicyPaymentDump.dump(modelPolicyPayment)
            dataResponse.append(UpdatePayment)

            # Insertamos en la tabla de policy
            modelPolicy = PolicyModel()
            id_policy = policy_payment["iddef_policy"]
            policyUpdate = modelPolicy.query.filter_by(
                iddef_policy=id_policy).first()
            PolicySchemaDump = PolicySchema(
                exclude=Util.get_default_excludes())

            policy = PolicySchemaDump.dump(policyUpdate)

            policyUpdate.policy_code = dataJson["policy_code"]

            db.session.flush()

            UpdatePolicy = PolicySchemaDump.dump(policyUpdate)
            dataResponse.append(UpdatePolicy)

            if UpdatePolicy and UpdatePayment:
                db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataResponse
            }

        except ValidationError as Error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": Error.messages,
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

    # @base.access_middleware
    def get(self):

        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.join(PolicyModel, and_(Model.iddef_policy == PolicyModel.iddef_policy))\
                    .add_columns(Model.iddef_policy_payment,PolicyModel.policy_code, Model.estado).all()
                schema = GetPolicyPaymentSchema(exclude=Util.get_default_excludes(), many=True)
                resp = schema.dump(data)
                
            else:
                data = Model.query.filter(Model.estado == 1)
                schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
                resp = schema.dump(data)

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
                        "data": resp
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                    "Error": True,
                    "data": {}
            }

        return response


class PolicyPaymentStatus(Resource):
    #api-policies-change-status
    # @base.access_middleware
    def put(self, id, estado):
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

            if estado == 0 or estado == 1:
                pass
            else:
                raise Exception("Status not valid")

            model.estado = estado
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

class PolicyPaymentListSearch(Resource):
    #api-policy-payment
    # @base.access_middleware
    def get(self, id):
        try:
           

            data = Model()
            data = Model.query.join(PolicyModel, and_(Model.iddef_policy == PolicyModel.iddef_policy))\
                    .add_columns(PolicyModel.policy_code,Model.iddef_policy_payment,Model.market_segment_list, Model.property_list, Model.description_en, Model.description_es,Model.estado).filter(Model.iddef_policy_payment == id).first()
            schema = GetPolicyPaymentSchema(exclude=Util.get_default_excludes())
            resp = schema.dump(data)

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
                        "data": resp
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                    "Error": True,
                    "data": {}
            }

        return response

class PolicyPaymentPublic(Resource):

    #api-policy-public
    @PublicAuth.access_middleware
    def get(self, country_code, lang):
        try:
            data = Model()
            id_market = Country.query.filter(Country.country_code == country_code, Country.estado == 1).first()
            data = Model.query.filter(Model.iddef_market_segment == id_market.idmarket_segment, Model.estado == 1).first()
            #schema = GetPolicyPaymentSchema(exclude=Util.get_default_excludes())
            #resp = schema.dump(data)
            resp = ""

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": ""
                }
            else:
                if lang.upper() == "ES":
                    resp = data.description_es
                else:
                    resp = data.description_en
                
                response = {
                    "Code": 200,
                    "Msg": "Success",
                        "Error": False,
                        "data": resp
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response



class PolicyPaymentPublicV2(Resource):
    #api-policy-public
    @PublicAuth.access_middleware
    def get(self, country_code, lang, property_code):
        try:
            data = Model()
            id_market = Country.query.filter(Country.country_code == country_code, Country.estado == 1).first()
            
            array_idmarket= []
            array_idmarket.append(id_market.idmarket_segment)

            pc = "\"" + property_code + "\""

            data_query= Model.query.filter(func.json_contains(Model.market_segment_list, str(id_market.idmarket_segment)), func.json_contains(Model.property_list, pc), Model.estado == 1 ).first()

            #data = Model.query.filter(Model.market_segment_list == id_market.idmarket_segment, Model.property_list ==  property_code,Model.estado == 1).first()
            schema = GetPolicyPaymentSchema(exclude=Util.get_default_excludes())
            data = schema.dump(data_query)
            resp = ""

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": ""
                }
            else:
                if lang.upper() == "ES":
                    resp = data["description_es"]
                else:
                    resp = data["description_en"]
                
                response = {
                    "Code": 200,
                    "Msg": "Success",
                        "Error": False,
                        "data": resp
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response


