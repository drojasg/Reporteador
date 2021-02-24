from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_cancel_penalty import PolicyCancelPenaltySchema as ModelSchema, PolicyCancelPenalty as Model, GetPolicyCancelPenaltySchema as GetModelSchema, PolicyCancelPenaltyDefaultSchema, GetPolicyCancelPenaltyDefaultSchema
from models.policy import Policy, PolicySchema, GetPolicySchema, GetPolicyCPSchema
from models.policy_penalty_cancel_fee import PolicyPenaltyCancelFee
from common.util import Util


class PolicyCancelPenalty(Resource):
    #api-policy_cancel_penalties-get-by-id
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

    #api-policy_cancel_penalties-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = PolicyCancelPenaltyDefaultSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            exists = Policy.query.filter(Policy.iddef_policy==data["iddef_policy"]).scalar() is not None

            if not exists:
                return {
                    "Code": 404,
                    "Msg": "Policy not found",
                    "Error": True,
                    "data": {}
                }

            model = Model()
            model.iddef_policy = data["iddef_policy"]
            model.penalty_name = data["penalty_name"]
            model.days_prior_to_arrival_deadline = data["days_prior_to_arrival_deadline"]
            model.time_date_deadline = data["time_date_deadline"]
            model.description_en = data["description_en"]
            model.description_es = data["description_es"]
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

    #api-policy_cancel_penalties-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetPolicyCancelPenaltyDefaultSchema(exclude=Util.get_default_excludes())
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
            
            if request.json.get("penalty_name") != None:
                model.penalty_name = data["penalty_name"]
            if request.json.get("days_prior_to_arrival_deadline") != None:
                model.days_prior_to_arrival_deadline = data["days_prior_to_arrival_deadline"]
            if request.json.get("time_date_deadline") != None:
                model.time_date_deadline = data["time_date_deadline"]
            if request.json.get("description_en") != None:
                model.description_en = data["description_en"]
            if request.json.get("description_es") != None:
                model.description_es = data["description_es"]
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


class PolicyCancelPenaltyDelete(Resource):
    #api-policy_cancel_penalties-delete
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

            # for id_cancel_fee, value_cancel_fee in enumerate(model.cancel_fees):
            #   model.cancel_fees[id_cancel_fee].estado = 0
            #   model.cancel_fees[id_cancel_fee].usuario_ultima_modificacion = user_name

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


class PolicyCancelPenaltyListSearch(Resource):
    #api-policy_cancel_penalties-get-all
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

    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetPolicyCPSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Policy.query.get(request.json.get("iddef_policy", 0))

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
    
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            # Nota: Los modelos nuevos se agregan fuera del loop debido a que al agregar un elemento nuevo
            # dentro del for se continuaba con el elemento agregado, generando un loop infinito 
            list_models_policy_cancel_penalties = []

            # Se procesan Penalidades
            for policy_cancel_penalty in request.json.get("policy_cancel_penalties", []):
                model_policy_cancel_penalty = Model()
                model_policy_cancel_penalty.penalty_name = policy_cancel_penalty["penalty_name"]
                model_policy_cancel_penalty.days_prior_to_arrival_deadline = policy_cancel_penalty["days_prior_to_arrival_deadline"]
                model_policy_cancel_penalty.time_date_deadline = policy_cancel_penalty["time_date_deadline"]
                model_policy_cancel_penalty.description_en = policy_cancel_penalty["description_en"]
                model_policy_cancel_penalty.description_es = policy_cancel_penalty["description_es"]
                model_policy_cancel_penalty.estado = 1
                model_policy_cancel_penalty.usuario_creacion = user_name
                # Se comentan las cancel_fees para separar APIs
                # for cancel_fee in policy_cancel_penalty["cancel_fees"]:
                #   model_cancel_fee = PolicyPenaltyCancelFee()
                #   model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                #   model_cancel_fee.percent = cancel_fee["percent"]
                #   model_cancel_fee.option_percent = cancel_fee["option_percent"]
                #   model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                #   model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                #   model_cancel_fee.estado = 1
                #   model_cancel_fee.usuario_creacion = user_name

                #   model_policy_cancel_penalty.cancel_fees.append(model_cancel_fee)

                list_models_policy_cancel_penalties.append(model_policy_cancel_penalty)

            for temp_policy_cancel_penalty in list_models_policy_cancel_penalties:
                model.policy_cancel_penalties.append(temp_policy_cancel_penalty)

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

class PolicyCancelPenaltyDefault(Resource):
    #api-policy_cancel_penalties-get-by-id-policy
    # @base.access_middleware
    def get(self, id_policy):
        try:
            schema = PolicyCancelPenaltyDefaultSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter(Model.iddef_policy==id_policy).all()

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
                    "data": schema.dump(data, many=True)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response