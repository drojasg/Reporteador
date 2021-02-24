from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_guarantee import PolicyGuaranteeSchema as ModelSchema, PolicyGuarantee as Model, GetPolicyGuaranteeSchema as GetModelSchema, DefaultPolicyGuaranteeSchema as DefaultSchema, GetPolicyGuaranteeDefaultSchema
from models.policy_guarantee_antifraud import PolicyGuaranteeAntifraud as ModelAntifraud
from common.util import Util


class PolicyGuarantee(Resource):
    #api-policy_guarantees-get-by-id
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

    #api-policy_guarantees-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetPolicyGuaranteeDefaultSchema(exclude=Util.get_default_excludes())
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
            if request.json.get("iddef_policy_guarantee_type") != None:
                model.iddef_policy_guarantee_type = data["iddef_policy_guarantee_type"]
            if request.json.get("allow_hold_free") != None:
                model.allow_hold_free = data["allow_hold_free"]
            if request.json.get("hold_duration") != None:
                model.hold_duration = data["hold_duration"]
            if request.json.get("stay_dates_option") != None:
                model.stay_dates_option = data["stay_dates_option"]
            if request.json.get("stay_dates") != None:
                model.stay_dates = data["stay_dates"]
            if request.json.get("reminder_lead_time") != None:
                model.reminder_lead_time = data["reminder_lead_time"]
            if request.json.get("offer_last_chance_promotion") != None:
                model.offer_last_chance_promotion = data["offer_last_chance_promotion"]
            if request.json.get("discount_per_night") != None:
                model.discount_per_night = data["discount_per_night"]
            if request.json.get("type_discount") != None:
                model.type_discount = data["type_discount"]
            if request.json.get("min_lead_time") != None:
                model.min_lead_time = data["min_lead_time"]
            if request.json.get("availability_threshold") != None:
                model.availability_threshold = data["availability_threshold"]
            if request.json.get("description_en") != None:
                model.description_en = data["description_en"]
            if request.json.get("description_es") != None:
                model.description_es = data["description_es"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            if request.json.get("nights_applied_antifraud") != None:
                model.nights_applied_antifraud = data["nights_applied_antifraud"]
            if request.json.get("policy_guarantee_antifrauds") != None:
                for guarantee_antifraud in data["policy_guarantee_antifrauds"]:
                    if guarantee_antifraud["iddef_policy_guarantee_antifraud"] == 0:
                        #Save antifraud
                        model_antifraud = ModelAntifraud()
                        model_antifraud.guarantee_nights_type = guarantee_antifraud["guarantee_nights_type"]
                        model_antifraud.guarantee_payment_type = guarantee_antifraud["guarantee_payment_type"]
                        model_antifraud.amount_payment = guarantee_antifraud["amount_payment"]
                        model_antifraud.currency_code = guarantee_antifraud["currency_code"]
                        model_antifraud.nights_payment = guarantee_antifraud["nights_payment"]
                        model_antifraud.estado = 1
                        model_antifraud.usuario_creacion = user_name

                        model.policy_guarantee_antifrauds.append(model_antifraud)
                    else:
                        #Update antifraud
                        for antifraud_index, antifraud_value in enumerate(model.policy_guarantee_antifrauds):
                            if antifraud_value.iddef_policy_guarantee_antifraud == guarantee_antifraud["iddef_policy_guarantee_antifraud"]:
                                model.policy_guarantee_antifrauds[antifraud_index].guarantee_nights_type = guarantee_antifraud["guarantee_nights_type"]
                                model.policy_guarantee_antifrauds[antifraud_index].guarantee_payment_type = guarantee_antifraud["guarantee_payment_type"]
                                model.policy_guarantee_antifrauds[antifraud_index].amount_payment = guarantee_antifraud["amount_payment"]
                                model.policy_guarantee_antifrauds[antifraud_index].currency_code = guarantee_antifraud["currency_code"]
                                model.policy_guarantee_antifrauds[antifraud_index].nights_payment = guarantee_antifraud["nights_payment"]
                                model.policy_guarantee_antifrauds[antifraud_index].estado = guarantee_antifraud["estado"]
                                model.policy_guarantee_antifrauds[antifraud_index].usuario_ultima_modificacion = user_name
                                break

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


class PolicyGuaranteeDelete(Resource):
    #api-policy_guarantees-delete
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


class PolicyGuaranteeListSearch(Resource):
    #api-policy_guarantees-get-all
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

    #api-policy_guarantees-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = DefaultSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)           
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            # model.iddef_policy_guarantee = data["iddef_policy_guarantee"]
            model.iddef_policy = data["iddef_policy"]
            model.iddef_policy_guarantee_type = data["iddef_policy_guarantee_type"]
            model.allow_hold_free = data["allow_hold_free"]
            model.hold_duration = data["hold_duration"]
            model.stay_dates_option = data["stay_dates_option"]
            model.stay_dates = data["stay_dates"] if(bool(data["stay_dates"])) else {"end": "", "start": ""}
            model.reminder_lead_time = data["reminder_lead_time"]
            model.offer_last_chance_promotion = data["offer_last_chance_promotion"]
            model.discount_per_night = data["discount_per_night"]
            model.type_discount = data["type_discount"]
            model.min_lead_time = data["min_lead_time"]
            model.availability_threshold = data["availability_threshold"]
            model.description_en = data["description_en"]
            model.description_es = data["description_es"]
            model.nights_applied_antifraud = data["nights_applied_antifraud"]
            if request.json.get("policy_guarantee_antifrauds") != None and len(data["policy_guarantee_antifrauds"]) > 0:
                for guarantee_antifraud in data["policy_guarantee_antifrauds"]:
                    #Save antifraud
                    model_antifraud = ModelAntifraud()
                    model_antifraud.guarantee_nights_type = guarantee_antifraud["guarantee_nights_type"]
                    model_antifraud.guarantee_payment_type = guarantee_antifraud["guarantee_payment_type"]
                    model_antifraud.amount_payment = guarantee_antifraud["amount_payment"]
                    model_antifraud.currency_code = guarantee_antifraud["currency_code"]
                    model_antifraud.nights_payment = guarantee_antifraud["nights_payment"]
                    model_antifraud.estado = 1
                    model_antifraud.usuario_creacion = user_name

                    model.policy_guarantee_antifrauds.append(model_antifraud)

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

